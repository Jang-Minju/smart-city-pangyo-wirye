import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { BoundaryEditor } from './components/BoundaryEditor.jsx';
import {
  ControlledDashboardMap,
  DashboardMap,
  DEVELOPMENT_MAIN_USE_LEGEND,
  LANDUSE_ZONE_LEGEND,
  getDevelopmentMainUseColor,
  getDevelopmentMainUseLabel,
} from './components/DashboardMap.jsx';
import './styles.css';

const dataUrl = (path) => `${import.meta.env.BASE_URL}${String(path).replace(/^\/+/, '')}`;

const tabs = [
  { id: 'landuse', label: '토지이용', eyebrow: 'Land Use', title: '토지이용 및 혼합 구조' },
  { id: 'development', label: '개발실현도', eyebrow: 'Development', title: '건축물과 업무시설 실현도' },
  { id: 'jobs', label: '직주·산업', eyebrow: 'Jobs & Industry', title: '직주균형과 산업 구성' },
  { id: 'accessibility', label: '접근성', eyebrow: 'Accessibility', title: '역세권과 광역 접근성' },
];

const kpis = [
  { label: '직주비', value: '판교 153.79 / 위례 0.21', hint: '고용 중심성 비교' },
  { label: '업무시설밀도', value: '판교 30,375 / 위례 4,152', hint: '㎡/ha' },
  { label: '업무시설 연면적비율', value: '판교 73.8% / 위례 18.1%', hint: '연면적 기준' },
  { label: '종사자 수', value: '판교 52,567 / 위례 25,567', hint: '명' },
  { label: '30분 도달 가능 종사자', value: '판교 191.8만 / 위례 148.2만', hint: '명' },
];

const tabDescriptions = {
  landuse: '용도지역과 blockType 레이어, LUM 비교 차트가 연결된 화면입니다.',
  development: '개발실현도 레이어와 건축물/필지 지도, 업무시설 실현 지표가 연결된 화면입니다.',
  jobs: 'SGIS 집계구 기반 인구·가구·사업체·종사자 분포와 산업특화를 비교하는 화면입니다.',
  accessibility: '역세권 buffer, 등시간권, 누적 접근성 곡선이 연결된 화면입니다.',
};

const defaultLanduseLayerVisibility = {
  zoning: true,
  blockType: false,
  station: true,
};

const defaultDevelopmentLayerVisibility = {
  buildingParcel: true,
  vacant: true,
  station: true,
};

const defaultJobsLayerVisibility = {
  census: true,
  station: true,
  metric: 'jobs_balance',
};

const landuseLayerOptions = [
  { id: 'zoning', label: '용도지역' },
  { id: 'blockType', label: 'blockType' },
  { id: 'station', label: '핵심역' },
];

const developmentLayerOptions = [
  { id: 'buildingParcel', label: '건축물/필지' },
  { id: 'vacant', label: '미건축·공지 추정' },
  { id: 'station', label: '핵심역' },
];

const jobsLayerOptions = [
  { id: 'census', label: 'SGIS 집계구' },
  { id: 'station', label: '핵심역' },
];

const jobsMetricOptions = [
  { id: 'jobs_balance', label: '직주균형' },
  { id: 'population_allocated', label: '인구' },
  { id: 'households_allocated', label: '가구' },
  { id: 'business_count_allocated', label: '사업체 수' },
  { id: 'worker_count_allocated', label: '종사자 수' },
];

const accessibilityTimeOptions = [
  { id: 'all', label: '전체' },
  { id: '30', label: '30분' },
  { id: '60', label: '60분' },
];

const defaultAccessibilityLayerVisibility = {
  station500m: false,
  station1km: false,
  station: true,
};

const accessibilityLayerOptions = [
  { id: 'station500m', label: '역세권 500m' },
  { id: 'station1km', label: '역세권 1km' },
  { id: 'station', label: '핵심역' },
];

const areaLabels = {
  pangyo_1st_technovalley: '판교',
  wirye_plan_area: '위례',
};

function parseCsv(text) {
  const rows = [];
  let current = '';
  let row = [];
  let inQuotes = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];

    if (char === '"') {
      if (inQuotes && next === '"') {
        current += '"';
        index += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === ',' && !inQuotes) {
      row.push(current);
      current = '';
      continue;
    }

    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && next === '\n') {
        index += 1;
      }
      row.push(current);
      rows.push(row);
      row = [];
      current = '';
      continue;
    }

    current += char;
  }

  if (current.length || row.length) {
    row.push(current);
    rows.push(row);
  }

  if (!rows.length) return [];
  const [headers, ...dataRows] = rows.filter((item) => item.length && item.some((value) => value !== ''));
  return dataRows.map((values) =>
    headers.reduce((result, header, index) => {
      result[header] = values[index] ?? '';
      return result;
    }, {}),
  );
}

function useLandusePanelData(enabled) {
  const [data, setData] = useState({
    zoningMix: [],
    blockTypeMix: [],
    zoningComposition: [],
    blockTypeComposition: [],
    coverageSummary: [],
    failed: false,
  });

  useEffect(() => {
    if (!enabled) return undefined;
    let ignore = false;

    async function loadData() {
      try {
        const responses = await Promise.all([
          fetch(dataUrl('data/landuse_mix_index.csv')),
          fetch(dataUrl('data/landuse_blocktype_mix_index.csv')),
          fetch(dataUrl('data/landuse_zone_composition.csv')),
          fetch(dataUrl('data/landuse_blocktype_composition.csv')),
          fetch(dataUrl('data/landuse_zone_coverage_summary.csv')),
        ]);
        if (responses.some((response) => !response.ok)) throw new Error('landuse panel data request failed');
        const [zoningMix, blockTypeMix, zoningComposition, blockTypeComposition, coverageSummary] = await Promise.all(
          responses.map((response) => response.text()),
        );
        if (!ignore) {
          setData({
            zoningMix: parseCsv(zoningMix),
            blockTypeMix: parseCsv(blockTypeMix),
            zoningComposition: parseCsv(zoningComposition),
            blockTypeComposition: parseCsv(blockTypeComposition),
            coverageSummary: parseCsv(coverageSummary),
            failed: false,
          });
        }
      } catch {
        if (!ignore) setData((current) => ({ ...current, failed: true }));
      }
    }

    loadData();
    return () => {
      ignore = true;
    };
  }, [enabled]);

  return data;
}

function useDevelopmentPanelData(enabled) {
  const [data, setData] = useState({ summary: [], composition: [], approvalTimeseries: [], failed: false });

  useEffect(() => {
    if (!enabled) return undefined;
    let ignore = false;

    async function loadData() {
      try {
        const responses = await Promise.all([
          fetch(dataUrl('data/development_summary.csv')),
          fetch(dataUrl('data/building_use_composition.csv')),
          fetch(dataUrl('data/building_approval_timeseries.csv')),
        ]);
        if (responses.some((response) => !response.ok)) throw new Error('development panel data request failed');
        const [summary, composition, approvalTimeseries] = await Promise.all(responses.map((response) => response.text()));
        if (!ignore) {
          setData({
            summary: parseCsv(summary),
            composition: parseCsv(composition),
            approvalTimeseries: parseCsv(approvalTimeseries),
            failed: false,
          });
        }
      } catch {
        if (!ignore) setData((current) => ({ ...current, failed: true }));
      }
    }

    loadData();
    return () => {
      ignore = true;
    };
  }, [enabled]);

  return data;
}

function useJobsPanelData(enabled) {
  const [data, setData] = useState({
    summary: [],
    jobsHousing: [],
    industryComposition: [],
    industryLq: [],
    topWorkerLq: [],
    failed: false,
  });

  useEffect(() => {
    if (!enabled) return undefined;
    let ignore = false;

    async function loadData() {
      try {
        const responses = await Promise.all([
          fetch(dataUrl('data/population_business_summary.csv')),
          fetch(dataUrl('data/jobs_housing_ratio.csv')),
          fetch(dataUrl('data/industry_basic_composition.csv')),
          fetch(dataUrl('data/industry_lq.csv')),
          fetch(dataUrl('data/top_worker_lq_industries.csv')),
        ]);
        if (responses.some((response) => !response.ok)) throw new Error('jobs panel data request failed');
        const [summary, jobsHousing, industryComposition, industryLq, topWorkerLq] = await Promise.all(
          responses.map((response) => response.text()),
        );
        if (!ignore) {
          setData({
            summary: parseCsv(summary),
            jobsHousing: parseCsv(jobsHousing),
            industryComposition: parseCsv(industryComposition),
            industryLq: parseCsv(industryLq),
            topWorkerLq: parseCsv(topWorkerLq),
            failed: false,
          });
        }
      } catch {
        if (!ignore) setData((current) => ({ ...current, failed: true }));
      }
    }

    loadData();
    return () => {
      ignore = true;
    };
  }, [enabled]);

  return data;
}

function useAccessibilityPanelData(enabled) {
  const [data, setData] = useState({
    summary: [],
    stationAreaRatio: [],
    cumulative: [],
    failed: false,
  });

  useEffect(() => {
    if (!enabled) return undefined;
    let ignore = false;

    async function loadData() {
      try {
        const responses = await Promise.all([
          fetch(dataUrl('data/accessibility_summary.csv')),
          fetch(dataUrl('data/station_area_ratio.csv')),
          fetch(dataUrl('data/accessibility_cumulative.csv')),
        ]);
        if (responses.some((response) => !response.ok)) throw new Error('accessibility panel data request failed');
        const [summary, stationAreaRatio, cumulative] = await Promise.all(responses.map((response) => response.text()));
        if (!ignore) {
          setData({
            summary: parseCsv(summary),
            stationAreaRatio: parseCsv(stationAreaRatio),
            cumulative: parseCsv(cumulative),
            failed: false,
          });
        }
      } catch {
        if (!ignore) setData((current) => ({ ...current, failed: true }));
      }
    }

    loadData();
    return () => {
      ignore = true;
    };
  }, [enabled]);

  return data;
}

function visibleAreasForView(viewMode) {
  if (viewMode === 'pangyo') return ['pangyo_1st_technovalley'];
  if (viewMode === 'wirye') return ['wirye_plan_area'];
  return ['pangyo_1st_technovalley', 'wirye_plan_area'];
}

function getAreaRow(rows, areaName) {
  return rows.find((row) => row.area_name === areaName);
}

function formatDecimal(value, digits = 6) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return number.toLocaleString('ko-KR', { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

function formatPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return `${(number * 100).toLocaleString('ko-KR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
}

function formatSqm(value, digits = 0) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return `${number.toLocaleString('ko-KR', { minimumFractionDigits: digits, maximumFractionDigits: digits })}㎡`;
}

function formatPeople(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return `${number.toLocaleString('ko-KR', { minimumFractionDigits: 3, maximumFractionDigits: 3 })}명`;
}

function formatWholePeople(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return `${Math.round(number).toLocaleString('ko-KR')}명`;
}

function formatHouseholds(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return `${number.toLocaleString('ko-KR', { minimumFractionDigits: 3, maximumFractionDigits: 3 })}가구`;
}

function formatBusinesses(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return `${number.toLocaleString('ko-KR', { minimumFractionDigits: 3, maximumFractionDigits: 3 })}개`;
}

function formatJobsHousingRatio(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  const digits = Math.abs(number) >= 1 ? 3 : 6;
  return number.toLocaleString('ko-KR', { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

function formatLq(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return number.toLocaleString('ko-KR', { minimumFractionDigits: 3, maximumFractionDigits: 6 });
}

function formatDensity(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return `${number.toLocaleString('ko-KR', { minimumFractionDigits: 3, maximumFractionDigits: 3 })}㎡/ha`;
}

function topCompositionRows(rows, areaName, categoryKey, ratioKey = 'area_ratio', valueKey = 'area_sqm') {
  const safeRows = Array.isArray(rows) ? rows : [];

  return safeRows
    .filter((row) => row.area_name === areaName)
    .sort((a, b) => Number(b[ratioKey]) - Number(a[ratioKey]))
    .slice(0, 6)
    .map((row) => ({
      category: row[categoryKey],
      ratio: row[ratioKey],
      value: row[valueKey],
    }));
}

const DEVELOPMENT_MAIN_USE_ORDER = DEVELOPMENT_MAIN_USE_LEGEND.map((item) => item.label);
const DEVELOPMENT_MAIN_USE_SET = new Set(DEVELOPMENT_MAIN_USE_ORDER);

function buildDevelopmentMainUseCompositionRows(rows, areaName, _categoryKey = 'main_use', ratioKey = 'area_ratio', valueKey = 'area_sqm') {
  const grouped = new Map(
    DEVELOPMENT_MAIN_USE_ORDER.map((label) => [label, { category: label, ratio: 0, value: 0 }]),
  );

  (Array.isArray(rows) ? rows : [])
    .filter((row) => row.area_name === areaName)
    .forEach((row) => {
      const label = getDevelopmentMainUseLabel(row.main_use);
      const category = DEVELOPMENT_MAIN_USE_SET.has(label) ? label : '기타';
      const target = grouped.get(category);
      if (!target) return;
      target.ratio += Number(row[ratioKey]) || 0;
      target.value += Number(row[valueKey]) || 0;
    });

  return DEVELOPMENT_MAIN_USE_ORDER
    .map((label) => grouped.get(label) ?? { category: label, ratio: 0, value: 0 })
    .filter((row) => Number(row.ratio) > 0 || row.category === '기타');
}

function getCategoryChipColor(category, categoryKey) {
  if (categoryKey === 'landuse_category') {
    const item = LANDUSE_ZONE_LEGEND.find((legend) => legend.label === category);
    return item ? `rgb(${item.color.join(',')})` : '#9aa6b2';
  }

  if (categoryKey === 'main_use') {
    const color = getDevelopmentMainUseColor(category);
    return `rgb(${color.slice(0, 3).join(',')})`;
  }

  const palette = ['#3676a9', '#7d8994', '#4092c3', '#60a874', '#a8997c', '#e5ae53', '#c65369', '#765ba4'];
  const hash = String(category ?? '').split('').reduce((sum, char) => sum + char.charCodeAt(0), 0);
  return palette[hash % palette.length];
}

function getJobsMetricLabel(metric) {
  return jobsMetricOptions.find((item) => item.id === metric)?.label ?? '직주균형';
}

function getLqDisplayRows(rows, areaName) {
  const cautionNames = new Set(['수도, 하수 및 폐기물 처리, 원료 재생업', '농업, 임업 및 어업']);
  return (Array.isArray(rows) ? rows : [])
    .filter((row) => row.area_name === areaName)
    .filter((row) => Number(row.worker_count) >= 100)
    .filter((row) => !cautionNames.has(row.industry_name))
    .slice(0, 4)
    .map((row) => ({
      industryName: row.industry_name,
      workerCount: row.worker_count,
      lq: row.lq,
    }));
}

function getAccessibilityRowsByArea(rows, areaName) {
  return (Array.isArray(rows) ? rows : [])
    .filter((row) => row.area_name === areaName)
    .sort((a, b) => Number(a.time_threshold_min) - Number(b.time_threshold_min));
}

function getAccessibilityRow(rows, areaName, threshold) {
  return (Array.isArray(rows) ? rows : []).find(
    (row) => row.area_name === areaName && String(row.time_threshold_min) === String(threshold),
  );
}

function getAccessibilityCumulativeRows(rows, areaName) {
  return (Array.isArray(rows) ? rows : [])
    .filter((row) => row.area_name === areaName)
    .sort((a, b) => Number(a.time_min) - Number(b.time_min))
    .map((row) => ({
      timeMin: Number(row.time_min) || 0,
      reachablePopulation: Number(row.reachable_population) || 0,
      reachableWorkers: Number(row.reachable_workers) || 0,
      stationName: row.station_name || row.origin_station || '',
    }));
}

function App() {
  const [activeTabId, setActiveTabId] = useState('landuse');
  const activeTab = useMemo(() => tabs.find((tab) => tab.id === activeTabId) ?? tabs[0], [activeTabId]);

  return (
    <main className="dashboard-shell">
      <Header activeTab={activeTab} />
      <section className="kpi-grid" aria-label="대시보드 KPI placeholder">
        {kpis.map((kpi) => (
          <article className="kpi-card" key={kpi.label}>
            <span>{kpi.label}</span>
            <strong>{kpi.value}</strong>
            <small>{kpi.hint}</small>
          </article>
        ))}
      </section>
      <DetailLayout activeTab={activeTab} activeTabId={activeTabId} setActiveTabId={setActiveTabId} />
    </main>
  );
}

function Header({ activeTab }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Urban Spatial Analytics Dashboard</p>
        <h1>판교 테크노밸리 vs 위례 계획구역</h1>
      </div>
      <div className="context-chip">
        <span>{activeTab.eyebrow}</span>
        <strong>{activeTab.label}</strong>
      </div>
    </header>
  );
}

function TabMenu({ activeTabId, setActiveTabId }) {
  return (
    <aside className="side-panel" aria-label="왼쪽 메뉴">
      <div className="panel-section">
        <h2>분석 탭</h2>
        <nav className="tab-list">
          {tabs.map((tab) => (
            <button
              className={tab.id === activeTabId ? 'tab-button active' : 'tab-button'}
              data-testid={`tab-${tab.id}`}
              key={tab.id}
              onClick={() => setActiveTabId(tab.id)}
              type="button"
            >
              <span>{tab.label}</span>
              <small>{tab.eyebrow}</small>
            </button>
          ))}
        </nav>
      </div>
    </aside>
  );
}

function OverviewLayout({ activeTab, activeTabId, setActiveTabId }) {
  return (
    <section className="overview-layout">
      <TabMenu activeTabId={activeTabId} setActiveTabId={setActiveTabId} />
      <div className="overview-main">
        <SectionTitle activeTab={activeTab} />
        <div className="split-map-grid">
          <DashboardMap initialView="pangyo" overlayTitle="판교 지도" overlayDescription="판교 제1테크노밸리 중심" />
          <DashboardMap initialView="wirye" overlayTitle="위례 지도" overlayDescription="위례 계획구역 중심" />
        </div>
        <div className="summary-strip">대시보드 개요 화면입니다. 종합 비교를 위한 기본 지도가 배치됩니다.</div>
      </div>
    </section>
  );
}

function DetailLayout({ activeTab, activeTabId, setActiveTabId }) {
  const [viewMode, setViewMode] = useState('comparison');
  const [landuseLayerVisibility, setLanduseLayerVisibility] = useState(defaultLanduseLayerVisibility);
  const [developmentLayerVisibility, setDevelopmentLayerVisibility] = useState(defaultDevelopmentLayerVisibility);
  const [jobsLayerVisibility, setJobsLayerVisibility] = useState(defaultJobsLayerVisibility);
  const [accessibilityLayerVisibility, setAccessibilityLayerVisibility] = useState(defaultAccessibilityLayerVisibility);
  const [accessibilityTimeMode, setAccessibilityTimeMode] = useState('all');
  const isLanduseTab = activeTab.id === 'landuse';
  const isDevelopmentTab = activeTab.id === 'development';
  const isJobsTab = activeTab.id === 'jobs';
  const isAccessibilityTab = activeTab.id === 'accessibility';
  const activeLayerVisibility = isLanduseTab
    ? landuseLayerVisibility
    : isDevelopmentTab
        ? developmentLayerVisibility
        : isJobsTab
          ? jobsLayerVisibility
          : isAccessibilityTab
            ? accessibilityLayerVisibility
        : landuseLayerVisibility;

  return (
    <section className="workspace-layout">
      <TabMenu activeTabId={activeTabId} setActiveTabId={setActiveTabId} />
      <div className="map-workspace">
        <SectionTitle activeTab={activeTab} />
        <div className="view-switch" aria-label="지도 보기 모드">
          <button className={viewMode === 'pangyo' ? 'active' : ''} onClick={() => setViewMode('pangyo')} type="button">
            판교 보기
          </button>
          <button className={viewMode === 'wirye' ? 'active' : ''} onClick={() => setViewMode('wirye')} type="button">
            위례 보기
          </button>
          <button className={viewMode === 'comparison' ? 'active' : ''} onClick={() => setViewMode('comparison')} type="button">
            비교 보기
          </button>
        </div>
        {isLanduseTab ? (
          <div className="map-layer-toggles" aria-label="토지이용 지도 레이어 토글">
            {landuseLayerOptions.map((option) => (
              <label key={option.id}>
                <input
                  checked={landuseLayerVisibility[option.id]}
                  onChange={() => setLanduseLayerVisibility((current) => ({ ...current, [option.id]: !current[option.id] }))}
                  type="checkbox"
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
        ) : null}
        {isDevelopmentTab ? (
          <div className="map-layer-toggles" aria-label="개발실현도 지도 레이어 토글">
            {developmentLayerOptions.map((option) => (
              <label key={option.id}>
                <input
                  checked={developmentLayerVisibility[option.id]}
                  onChange={() => setDevelopmentLayerVisibility((current) => ({ ...current, [option.id]: !current[option.id] }))}
                  type="checkbox"
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
        ) : null}
        {isJobsTab ? (
          <>
            <div className="metric-switch" aria-label="직주·산업 지도 지표 선택">
              {jobsMetricOptions.map((option) => (
                <button
                  className={jobsLayerVisibility.metric === option.id ? 'active' : ''}
                  key={option.id}
                  onClick={() => setJobsLayerVisibility((current) => ({ ...current, metric: option.id }))}
                  type="button"
                >
                  {option.label}
                </button>
              ))}
            </div>
            <div className="map-layer-toggles" aria-label="직주·산업 지도 레이어 토글">
              {jobsLayerOptions.map((option) => (
                <label key={option.id}>
                  <input
                    checked={jobsLayerVisibility[option.id]}
                    onChange={() => setJobsLayerVisibility((current) => ({ ...current, [option.id]: !current[option.id] }))}
                    type="checkbox"
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
          </>
        ) : null}
        {isAccessibilityTab ? (
          <>
            <div className="metric-switch" aria-label="접근성 시간대 선택">
              {accessibilityTimeOptions.map((option) => (
                <button
                  className={accessibilityTimeMode === option.id ? 'active' : ''}
                  key={option.id}
                  onClick={() =>
                    setAccessibilityTimeMode((current) => (current === option.id ? null : option.id))
                  }
                  type="button"
                >
                  {option.label}
                </button>
              ))}
            </div>
            <div className="map-layer-toggles" aria-label="접근성 보조 레이어 토글">
              {accessibilityLayerOptions.map((option) => (
                <label key={option.id}>
                  <input
                    checked={accessibilityLayerVisibility[option.id]}
                    onChange={() => setAccessibilityLayerVisibility((current) => ({ ...current, [option.id]: !current[option.id] }))}
                    type="checkbox"
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
          </>
        ) : null}
        <DetailMapArea
          accessibilityTimeMode={accessibilityTimeMode}
          activeTab={activeTab}
          layerVisibility={activeLayerVisibility}
          viewMode={viewMode}
        />
      </div>
      <AnalysisPanel activeTab={activeTab} viewMode={viewMode} accessibilityTimeMode={accessibilityTimeMode} />
    </section>
  );
}

function DetailMapArea({ activeTab, layerVisibility, viewMode, accessibilityTimeMode }) {
  const analysisLayer =
    activeTab.id === 'landuse'
      ? 'landuse'
      : activeTab.id === 'development'
        ? 'development'
        : activeTab.id === 'jobs'
          ? 'jobs'
          : activeTab.id === 'accessibility'
            ? 'accessibility'
            : 'base';

  if (viewMode === 'comparison') {
    return (
      <div className="detail-comparison-area">
        <div className="detail-split-map-grid">
          <DashboardMap
            accessibilityTimeMode={accessibilityTimeMode}
            analysisLayer={analysisLayer}
            initialView="pangyo"
            jobsMetric={analysisLayer === 'jobs' ? layerVisibility.metric : undefined}
            layerVisibility={layerVisibility}
            overlayTitle="판교 제1테크노밸리"
            overlayDescription={
              analysisLayer === 'landuse'
                ? '토지이용 레이어 기준 판교'
                : analysisLayer === 'development'
                  ? '개발실현도 레이어 기준 판교'
                : analysisLayer === 'jobs'
                  ? `${getJobsMetricLabel(layerVisibility.metric)} 기준 판교`
                  : analysisLayer === 'accessibility'
                    ? '핵심역 기준 등시간권 판교'
                    : '경계와 핵심역 중심 판교'
            }
            showDetailedLegend={analysisLayer !== 'landuse'}
          />
          <DashboardMap
            accessibilityTimeMode={accessibilityTimeMode}
            analysisLayer={analysisLayer}
            initialView="wirye"
            jobsMetric={analysisLayer === 'jobs' ? layerVisibility.metric : undefined}
            layerVisibility={layerVisibility}
            overlayTitle="위례 계획구역"
            overlayDescription={
              analysisLayer === 'landuse'
                ? '토지이용 레이어 기준 위례'
                : analysisLayer === 'development'
                  ? '개발실현도 레이어 기준 위례'
                : analysisLayer === 'jobs'
                  ? `${getJobsMetricLabel(layerVisibility.metric)} 기준 위례`
                  : analysisLayer === 'accessibility'
                    ? '핵심역 기준 등시간권 위례'
                    : '경계와 핵심역 중심 위례'
            }
            showDetailedLegend={analysisLayer !== 'landuse'}
          />
        </div>
        {analysisLayer === 'landuse' ? (
          <div className="comparison-placeholder">토지이용은 좌우 동일한 색상 체계로 비교합니다.</div>
        ) : analysisLayer === 'development' ? (
          <div className="comparison-placeholder">개발실현도는 건축물/필지와 미건축·공지 추정 필지를 같은 기준으로 비교합니다.</div>
        ) : analysisLayer === 'jobs' ? (
          <div className="comparison-placeholder">
            {`${getJobsMetricLabel(layerVisibility.metric)} 기준 공통 스케일로 판교와 위례를 비교합니다. 판교는 상주인구는 매우 적지만 종사자 수와 직주비가 높아 고용 중심지 성격이 강하고, 위례는 상주인구와 가구 수가 많고 직주비가 낮아 주거 중심 신도시 성격이 강합니다.`}
          </div>
        ) : analysisLayer === 'accessibility' ? (
          <div className="comparison-placeholder">핵심역을 기준으로 30분·60분 이내 도달 가능한 범위와 인구·종사자 규모를 비교합니다.</div>
        ) : (
          <div className="comparison-placeholder">토지이용, 개발실현도, 직주·산업, 접근성 비교 지표가 단계별로 연결될 예정입니다.</div>
        )}
      </div>
    );
  }

  return (
    <ControlledDashboardMap
      accessibilityTimeMode={accessibilityTimeMode}
      analysisLayer={analysisLayer}
      jobsMetric={analysisLayer === 'jobs' ? layerVisibility.metric : undefined}
      layerVisibility={layerVisibility}
      viewMode={viewMode}
      overlayTitle={`${activeTab.label} 지도`}
      overlayDescription="VWorld 베이스맵 위에 분석 레이어를 표시합니다."
    />
  );
}

function SectionTitle({ activeTab }) {
  return (
    <div className="section-title">
      <p>{activeTab.eyebrow}</p>
      <h2>{activeTab.title}</h2>
      <span>{tabDescriptions[activeTab.id]}</span>
    </div>
  );
}

function AnalysisPanel({ activeTab, viewMode, accessibilityTimeMode }) {
  if (activeTab.id === 'development') {
    return <DevelopmentAnalysisPanel viewMode={viewMode} />;
  }
  if (activeTab.id === 'landuse') {
    return <LanduseAnalysisPanel viewMode={viewMode} />;
  }
  if (activeTab.id === 'jobs') {
    return <JobsAnalysisPanel viewMode={viewMode} />;
  }
  if (activeTab.id === 'accessibility') {
    return <AccessibilityAnalysisPanel viewMode={viewMode} accessibilityTimeMode={accessibilityTimeMode} />;
  }

  return (
    <aside className="analysis-panel" aria-label="분석 패널 placeholder">
      <div className="panel-heading">
        <p>{activeTab.eyebrow}</p>
        <h2>{activeTab.label} 분석 패널</h2>
      </div>
      <div className="placeholder-card tall">
        <span>차트 placeholder</span>
        <div className="bar-skeleton" />
        <div className="bar-skeleton short" />
        <div className="bar-skeleton medium" />
      </div>
      <div className="placeholder-card">
        <span>지표표 placeholder</span>
        <div className="table-skeleton" />
      </div>
      <div className="placeholder-card">
        <span>해설문 placeholder</span>
        <p>{tabDescriptions[activeTab.id]}</p>
      </div>
    </aside>
  );
}

function AccessibilityAnalysisPanel({ viewMode, accessibilityTimeMode }) {
  const data = useAccessibilityPanelData(true);
  const areas = visibleAreasForView(viewMode);

  return (
    <aside className="analysis-panel" aria-label="접근성 분석 패널">
      <div className="panel-heading">
        <p>Accessibility</p>
        <h2>대중교통 접근성 및 등시간권</h2>
      </div>
      <div className="development-summary-note">
        핵심역을 기준으로 30분·60분 이내 도달 가능한 범위와 인구·종사자 규모를 비교합니다.
      </div>
      {data.failed ? <div className="panel-alert">접근성 데이터를 불러오지 못했습니다.</div> : null}
      <div className={areas.length > 1 ? 'jobs-metric-grid comparison' : 'jobs-metric-grid'}>
        {areas.map((areaName) => {
          const row30 = getAccessibilityRow(data.summary, areaName, 30);
          const row60 = getAccessibilityRow(data.summary, areaName, 60);
          const rows = accessibilityTimeMode === '30' ? [row30] : accessibilityTimeMode === '60' ? [row60] : [row30, row60];

          return (
            <div className="jobs-area-card" key={areaName}>
              <span>{areaLabels[areaName]}</span>
              {rows.filter(Boolean).map((row) => (
                <React.Fragment key={`${areaName}-${row.time_threshold_min}`}>
                  <div className="jobs-metric-row">
                    <small>{`${row.time_threshold_min}분 도달 가능 인구`}</small>
                    <strong>{formatPeople(row.reachable_population)}</strong>
                  </div>
                  <div className="jobs-metric-row">
                    <small>{`${row.time_threshold_min}분 도달 가능 종사자`}</small>
                    <strong>{formatPeople(row.reachable_workers)}</strong>
                  </div>
                </React.Fragment>
              ))}
            </div>
          );
        })}
      </div>
      <div className="development-interpretation">
        <p>판교는 30분·60분 도달 가능 종사자 규모가 위례보다 커 업무 중심지 접근성이 강하다. 위례는 주거 중심 신도시 성격이 강하고, 핵심역 접근권은 존재하지만 판교보다 업무 접근성 지표가 낮다.</p>
      </div>
      <div className="placeholder-card composition-card">
        <span>역세권 보조 지표</span>
        <div className={areas.length > 1 ? 'composition-columns' : 'composition-columns single'}>
          {areas.map((areaName) => {
            const row = getAreaRow(data.stationAreaRatio, areaName);
            return (
              <div className="composition-column" key={areaName}>
                <strong>{areaLabels[areaName]}</strong>
                <div className="composition-row">
                  <span className="composition-left">
                    <span>500m 내 면적 비율</span>
                  </span>
                  <small className="composition-sub">{formatPercent(row?.buffer_500m_area_ratio)}</small>
                </div>
                <div className="composition-row">
                  <span className="composition-left">
                    <span>1km 내 면적 비율</span>
                  </span>
                  <small className="composition-sub">{formatPercent(row?.buffer_1km_area_ratio)}</small>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <AccessibilityCurvePanel areas={areas} rows={data.cumulative} />
    </aside>
  );
}

function LanduseAnalysisPanel({ viewMode }) {
  const data = useLandusePanelData(true);
  const areas = visibleAreasForView(viewMode);

  return (
    <aside className="analysis-panel" aria-label="토지이용 분석 패널">
      <div className="panel-heading">
        <p>Land Use</p>
        <h2>토지이용 분석 패널</h2>
      </div>
      {data.failed ? <div className="panel-alert">토지이용 데이터를 불러오지 못했습니다.</div> : null}
      <div className={areas.length > 1 ? 'landuse-metric-grid comparison' : 'landuse-metric-grid'}>
        {areas.map((areaName) => {
          const zoning = getAreaRow(data.zoningMix, areaName);
          const blockType = getAreaRow(data.blockTypeMix, areaName);
          const coverage = getAreaRow(data.coverageSummary, areaName);

          return (
            <div className="landuse-area-card" key={areaName}>
              <span>{areaLabels[areaName]}</span>
              <div className="landuse-metric-row">
                <small>zoning LUM</small>
                <strong>{formatDecimal(zoning?.lum_index)}</strong>
              </div>
              <div className="landuse-metric-row">
                <small>blockType LUM</small>
                <strong>{formatDecimal(blockType?.lum_index)}</strong>
              </div>
              <div className="landuse-metric-row">
                <small>coverage</small>
                <strong>{formatDecimal(coverage?.coverage_ratio)}</strong>
              </div>
              {areaName === 'wirye_plan_area' ? (
                <div className="landuse-metric-row">
                  <small>남은 결측 면적</small>
                  <strong>{formatSqm(coverage?.missing_area_sqm, 0)}</strong>
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
      <CompositionSection
        areas={areas}
        categoryKey="landuse_category"
        rows={data.zoningComposition}
        title="용도지역 구성비"
      />
      <PieComparisonChart
        areas={areas}
        rows={data.zoningComposition}
        categoryKey="landuse_category"
        title="용도지역 구성비 차트"
      />
    </aside>
  );
}

function DevelopmentAnalysisPanel({ viewMode }) {
  const data = useDevelopmentPanelData(true);
  const areas = visibleAreasForView(viewMode);

  return (
    <aside className="analysis-panel" aria-label="개발실현도 분석 패널">
      <div className="panel-heading">
        <p>Development</p>
        <h2>개발실현도 분석 패널</h2>
      </div>
      <div className="development-summary-note">
        개발실현도는 계획된 토지가 실제 건축물과 업무기능으로 얼마나 구현되었는지를 보는 지표입니다.
        본 화면에서는 개발필지비율, 미건축·공지 추정비율, 업무시설 연면적비율, 업무시설밀도를 중심으로 비교합니다.
      </div>
      {data.failed ? <div className="panel-alert">개발실현도 데이터를 불러오지 못했습니다.</div> : null}
      <div className={areas.length > 1 ? 'development-metric-grid comparison' : 'development-metric-grid'}>
        {areas.map((areaName) => {
          const summary = getAreaRow(data.summary, areaName);
          return (
            <div className="development-area-card" key={areaName}>
              <span>{areaLabels[areaName]}</span>
              <div className="development-metric-row">
                <small>개발필지비율</small>
                <strong>{formatDecimal(summary?.developed_parcel_ratio)}</strong>
              </div>
              <div className="development-metric-row">
                <small>미건축·공지 추정비율</small>
                <strong>{formatDecimal(summary?.estimated_unbuilt_parcel_ratio)}</strong>
              </div>
              <div className="development-metric-row">
                <small>업무시설 연면적비율</small>
                <strong>{formatDecimal(summary?.business_floor_area_ratio)}</strong>
              </div>
              <div className="development-metric-row">
                <small>업무시설밀도</small>
                <strong>{formatDensity(summary?.business_floor_area_density_sqm_per_ha)}</strong>
              </div>
            </div>
          );
        })}
      </div>
      <div className="development-interpretation">
        {viewMode === 'pangyo' ? (
          <p>판교는 업무시설 연면적비율과 업무시설밀도가 높아 실제 업무·고용 중심지로 실현된 성격이 강하다.</p>
        ) : viewMode === 'wirye' ? (
          <p>위례는 개발은 진행되었지만 업무시설 비중과 업무시설밀도가 낮아 주거 중심 신도시 성격이 강하다.</p>
        ) : (
          <p>판교는 업무시설 연면적비율과 업무시설밀도가 높아 실제 업무 중심지로 실현된 지역이고, 위례는 개발필지비율은 확인되지만 업무시설 비중과 밀도가 낮아 주거 중심 성격이 강한 지역이다.</p>
        )}
      </div>
      <CompositionSection
        areas={areas}
        categoryKey="main_use"
        rows={data.composition}
        ratioKey="floor_area_ratio"
        valueKey="total_floor_area_sqm"
        title="건축물 용도 구성비 — 연면적 기준"
        rowBuilder={buildDevelopmentMainUseCompositionRows}
      />
      <PieComparisonChart
        areas={areas}
        rows={data.composition}
        categoryKey="main_use"
        ratioKey="floor_area_ratio"
        valueKey="total_floor_area_sqm"
        title="건축물 용도 구성비 차트 — 연면적 기준"
        rowBuilder={buildDevelopmentMainUseCompositionRows}
      />
    </aside>
  );
}

function JobsAnalysisPanel({ viewMode }) {
  const data = useJobsPanelData(true);
  const areas = visibleAreasForView(viewMode);

  return (
    <aside className="analysis-panel" aria-label="직주·산업 분석 패널">
      <div className="panel-heading">
        <p>Jobs & Industry</p>
        <h2>직주·산업 분석 패널</h2>
      </div>
      <div className="development-summary-note">
        직주·산업 분석은 상주인구와 고용 규모의 균형, 그리고 산업별 종사자 집중도를 통해 지역의 기능적 성격을 비교한다.
        판교는 종사자 수와 직주비가 매우 높아 고용 중심지 성격이 강하고, 위례는 상주인구가 많고 직주비가 낮아 주거 중심 신도시 성격이 강하다.
      </div>
      {data.failed ? <div className="panel-alert">직주·산업 데이터를 불러오지 못했습니다.</div> : null}
      <div className={areas.length > 1 ? 'jobs-metric-grid comparison' : 'jobs-metric-grid'}>
        {areas.map((areaName) => {
          const summary = getAreaRow(data.summary, areaName);
          const jobsHousing = getAreaRow(data.jobsHousing, areaName);
          return (
            <div className="jobs-area-card" key={areaName}>
              <span>{areaLabels[areaName]}</span>
              <div className="jobs-metric-row">
                <small>인구</small>
                <strong>{formatPeople(summary?.population)}</strong>
              </div>
              <div className="jobs-metric-row">
                <small>가구</small>
                <strong>{formatHouseholds(summary?.households)}</strong>
              </div>
              <div className="jobs-metric-row">
                <small>사업체 수</small>
                <strong>{formatBusinesses(summary?.business_count)}</strong>
              </div>
              <div className="jobs-metric-row">
                <small>종사자 수</small>
                <strong>{formatPeople(summary?.worker_count)}</strong>
              </div>
              <div className="jobs-metric-row">
                <small>직주비</small>
                <strong>{formatJobsHousingRatio(jobsHousing?.jobs_housing_ratio)}</strong>
              </div>
            </div>
          );
        })}
      </div>
      <div className="development-interpretation">
        {viewMode === 'pangyo' ? (
          <p>판교는 인구보다 종사자 수가 압도적으로 많고, 정보통신업과 전문·과학·기술서비스업 중심의 고용 특화가 나타난다.</p>
        ) : viewMode === 'wirye' ? (
          <p>위례는 상주인구와 가구 규모가 크지만 종사자 수가 상대적으로 적고, 교육·보건·생활서비스 업종 비중이 상대적으로 높다.</p>
        ) : (
          <p>판교는 인구보다 종사자 수가 압도적으로 많아 업무·고용 중심성이 강하고, 위례는 인구와 가구 규모가 크지만 종사자 수가 상대적으로 적어 주거 중심성이 강하다. 판교는 정보통신업과 전문기술서비스업 중심의 고용 특화가 나타나고, 위례는 교육·보건·생활서비스 업종 비중이 상대적으로 높다.</p>
        )}
      </div>
      <LqSection areas={areas} rows={data.topWorkerLq} />
      <CompositionSection
        areas={areas}
        categoryKey="industry_name"
        rows={data.industryComposition.filter((row) => row.metric_type === 'worker_count')}
        ratioKey="ratio"
        valueKey="value"
        title="종사자 기준 산업구성"
        description="산업구성 색상칩은 사용하지 않으며, 지도 색상은 선택한 SGIS 지표 또는 직주균형 유형을 나타냅니다."
        valueFormatter={formatPeople}
        showChip={false}
      />
      <JobsIndustryBarChart rows={data.industryComposition} />
      <div className="panel-note">
        <span className="panel-note-chip warning" />
        <p>소규모 종사자 기반 LQ는 과대해석하지 않는다. 판교의 수도·하수·폐기물처리업과 위례의 농업·임업·어업은 보조 참고값으로만 본다.</p>
      </div>
    </aside>
  );
}

function LqSection({ areas, rows }) {
  return (
    <div className="placeholder-card composition-card lq-card">
      <span>산업특화도 LQ</span>
      <p className="composition-description">LQ는 두 지역 전체 산업구성 대비 특정 지역에서 해당 산업이 얼마나 집중되어 있는지를 나타내는 지표입니다.</p>
      <div className={areas.length > 1 ? 'lq-columns' : 'lq-columns single'}>
        {areas.map((areaName) => (
          <div className="lq-column" key={areaName}>
            <strong>{`${areaLabels[areaName]} 특화산업`}</strong>
            {getLqDisplayRows(rows, areaName).slice(0, 3).map((row, index) => (
              <div className="lq-row" key={`${areaName}-${row.industryName}`}>
                <div className="lq-row-head">
                  <span className="lq-rank">{index + 1}.</span>
                  <span className="lq-industry" title={row.industryName}>{row.industryName}</span>
                </div>
                <div className="lq-row-meta">
                  <span className="lq-badge">{`LQ ${formatLq(row.lq)}`}</span>
                  <small>{formatPeople(row.workerCount)}</small>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

function polarToCartesian(cx, cy, radius, angleDeg) {
  const angle = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: cx + radius * Math.cos(angle),
    y: cy + radius * Math.sin(angle),
  };
}

function describeArc(cx, cy, radius, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, radius, endAngle);
  const end = polarToCartesian(cx, cy, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
  return `M ${cx} ${cy} L ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArcFlag} 0 ${end.x} ${end.y} Z`;
}

function ChartHoverTooltip({ tooltip }) {
  if (!tooltip?.visible) return null;

  return (
    <div
      className="chart-hover-tooltip"
      style={{
        left: `${tooltip.x}px`,
        top: `${tooltip.y}px`,
      }}
    >
      {tooltip.title ? <strong>{tooltip.title}</strong> : null}
      {Array.isArray(tooltip.rows)
        ? tooltip.rows.map((row) => (
            <div key={`${tooltip.title}-${row.label}-${row.value}`}>
              <span>{row.label}</span>
              <b>{row.value}</b>
            </div>
          ))
        : null}
    </div>
  );
}

function getChartTooltipPosition(event, preferredWidth = 220, preferredHeight = 120) {
  const gap = 14;
  const viewportWidth = typeof window !== 'undefined' ? window.innerWidth : 1280;
  const viewportHeight = typeof window !== 'undefined' ? window.innerHeight : 800;

  let x = event.clientX + gap;
  let y = event.clientY + gap;

  if (x + preferredWidth > viewportWidth - 8) {
    x = event.clientX - preferredWidth - gap;
  }

  if (y + preferredHeight > viewportHeight - 8) {
    y = event.clientY - preferredHeight - gap;
  }

  x = Math.max(8, Math.min(x, viewportWidth - preferredWidth - 8));
  y = Math.max(8, Math.min(y, viewportHeight - preferredHeight - 8));

  return { x, y };
}

function PieComparisonChart({
  areas,
  rows,
  categoryKey,
  ratioKey = 'area_ratio',
  valueKey = 'area_sqm',
  rowBuilder = topCompositionRows,
  title,
}) {
  const safeAreas = Array.isArray(areas) ? areas : [];
  const safeRows = Array.isArray(rows) ? rows : [];
  const [tooltip, setTooltip] = useState(null);

  function showTooltip(event, title, rowsData) {
    const { x, y } = getChartTooltipPosition(event);
    setTooltip({
      visible: true,
      x,
      y,
      title,
      rows: rowsData,
    });
  }

  return (
    <div className="placeholder-card chart-card">
      <span>{title}</span>
      <ChartHoverTooltip tooltip={tooltip} />
      <div className={safeAreas.length > 1 ? 'pie-chart-grid' : 'pie-chart-grid single'}>
        {safeAreas.map((areaName) => {
          const chartRows = rowBuilder(safeRows, areaName, categoryKey, ratioKey, valueKey)
            .filter((row) => Number(row.ratio) > 0)
            .slice(0, 6);
          const total = chartRows.reduce((sum, row) => sum + (Number(row.ratio) || 0), 0);
          let angle = 0;

          return (
            <div className="pie-chart-panel" key={`${title}-${areaName}`}>
              <strong>{areaLabels[areaName]}</strong>
              <svg className="pie-chart-svg" viewBox="0 0 160 160" aria-hidden="true">
                <circle cx="80" cy="80" fill="#f5f7fa" r="54" stroke="#d7e0e7" strokeWidth="1" />
                {chartRows.map((row) => {
                  const displayCategory = categoryKey === 'main_use' ? getDevelopmentMainUseLabel(row.category) : row.category;
                  const ratio = total > 0 ? (Number(row.ratio) || 0) / total : 0;
                  const nextAngle = angle + ratio * 360;
                  const path = describeArc(80, 80, 54, angle, nextAngle);
                  angle = nextAngle;
                  return (
                    <path
                      d={path}
                      fill={getCategoryChipColor(displayCategory, categoryKey)}
                      key={`${areaName}-${displayCategory}`}
                      onMouseEnter={(event) =>
                        showTooltip(event, areaLabels[areaName], [
                          { label: categoryKey === 'main_use' ? '건축물 주용도' : '용도지역명', value: displayCategory },
                          { label: '비율', value: formatPercent(row.ratio) },
                          {
                            label: valueKey === 'total_floor_area_sqm' ? '연면적' : '면적',
                            value: formatSqm(row.value),
                          },
                        ])
                      }
                      onMouseLeave={() => setTooltip(null)}
                      onMouseMove={(event) =>
                        showTooltip(event, areaLabels[areaName], [
                          { label: categoryKey === 'main_use' ? '건축물 주용도' : '용도지역명', value: displayCategory },
                          { label: '비율', value: formatPercent(row.ratio) },
                          {
                            label: valueKey === 'total_floor_area_sqm' ? '연면적' : '면적',
                            value: formatSqm(row.value),
                          },
                        ])
                      }
                      stroke="#ffffff"
                      strokeWidth="1.5"
                    />
                  );
                })}
                <circle cx="80" cy="80" fill="#ffffff" r="24" />
              </svg>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function JobsIndustryBarChart({ rows }) {
  const safeRows = Array.isArray(rows) ? rows.filter((row) => row.metric_type === 'worker_count') : [];
  const categoryMap = new Map();
  const [tooltip, setTooltip] = useState(null);

  function showTooltip(event, title, rowsData) {
    const { x, y } = getChartTooltipPosition(event);
    setTooltip({
      visible: true,
      x,
      y,
      title,
      rows: rowsData,
    });
  }

  safeRows.forEach((row) => {
    if (!['pangyo_1st_technovalley', 'wirye_plan_area'].includes(row.area_name)) return;
    const entry = categoryMap.get(row.industry_name) ?? {
      category: row.industry_name,
      pangyo: 0,
      wirye: 0,
      pangyoValue: 0,
      wiryeValue: 0,
      total: 0,
    };
    const ratio = Number(row.ratio) || 0;
    if (row.area_name === 'pangyo_1st_technovalley') entry.pangyo = ratio;
    if (row.area_name === 'wirye_plan_area') entry.wirye = ratio;
    if (row.area_name === 'pangyo_1st_technovalley') entry.pangyoValue = Number(row.value) || 0;
    if (row.area_name === 'wirye_plan_area') entry.wiryeValue = Number(row.value) || 0;
    entry.total = entry.pangyo + entry.wirye;
    categoryMap.set(row.industry_name, entry);
  });

  const chartRows = Array.from(categoryMap.values())
    .sort((a, b) => b.total - a.total)
    .slice(0, 5);
  const maxValue = Math.max(0.01, ...chartRows.flatMap((row) => [row.pangyo, row.wirye]));

  return (
    <div className="placeholder-card chart-card">
      <span>종사자 기준 산업구성 비교</span>
      <ChartHoverTooltip tooltip={tooltip} />
      <div className="bar-chart-list">
        {chartRows.map((row) => (
          <div className="bar-chart-row" key={row.category}>
            <strong title={row.category}>{row.category}</strong>
            <div className="bar-chart-bars">
              <div
                className="bar-track"
                onMouseEnter={(event) =>
                  showTooltip(event, '판교', [
                    { label: '산업명', value: row.category },
                    { label: '종사자 비율', value: formatPercent(row.pangyo) },
                    { label: '종사자 수', value: formatPeople(row.pangyoValue) },
                  ])
                }
                onMouseLeave={() => setTooltip(null)}
                onMouseMove={(event) =>
                  showTooltip(event, '판교', [
                    { label: '산업명', value: row.category },
                    { label: '종사자 비율', value: formatPercent(row.pangyo) },
                    { label: '종사자 수', value: formatPeople(row.pangyoValue) },
                  ])
                }
              >
                <div className="bar-fill pangyo" style={{ width: `${(row.pangyo / maxValue) * 100}%` }} />
              </div>
              <span>{formatPercent(row.pangyo)}</span>
            </div>
            <div className="bar-chart-bars">
              <div
                className="bar-track"
                onMouseEnter={(event) =>
                  showTooltip(event, '위례', [
                    { label: '산업명', value: row.category },
                    { label: '종사자 비율', value: formatPercent(row.wirye) },
                    { label: '종사자 수', value: formatPeople(row.wiryeValue) },
                  ])
                }
                onMouseLeave={() => setTooltip(null)}
                onMouseMove={(event) =>
                  showTooltip(event, '위례', [
                    { label: '산업명', value: row.category },
                    { label: '종사자 비율', value: formatPercent(row.wirye) },
                    { label: '종사자 수', value: formatPeople(row.wiryeValue) },
                  ])
                }
              >
                <div className="bar-fill wirye" style={{ width: `${(row.wirye / maxValue) * 100}%` }} />
              </div>
              <span>{formatPercent(row.wirye)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AccessibilityCurvePanel({ areas, rows }) {
  const safeAreas = Array.isArray(areas) ? areas : [];
  const pangyoRows = getAccessibilityCumulativeRows(rows, 'pangyo_1st_technovalley');
  const wiryeRows = getAccessibilityCumulativeRows(rows, 'wirye_plan_area');

  return (
    <div className="placeholder-card chart-card">
      <span>누적 접근성 곡선</span>
      <LineComparisonChart
        title="누적 도달 가능 인구"
        unitLabel="명"
        valueKey="reachablePopulation"
        pangyoRows={pangyoRows}
        wiryeRows={wiryeRows}
        visibleAreas={safeAreas}
      />
      <LineComparisonChart
        title="누적 도달 가능 종사자"
        unitLabel="명"
        valueKey="reachableWorkers"
        pangyoRows={pangyoRows}
        wiryeRows={wiryeRows}
        visibleAreas={safeAreas}
      />
      <p className="chart-footnote">
        판교는 30분 이후 접근 가능한 종사자 규모가 빠르게 증가하며, 위례보다 고용 접근성이 높게 나타난다. 위례도 60분권에서는 넓은 접근 범위를 가지지만, 업무 중심 접근성은 판교보다 낮다.
      </p>
    </div>
  );
}

function LineComparisonChart({ title, unitLabel, valueKey, pangyoRows, wiryeRows, visibleAreas }) {
  const [tooltip, setTooltip] = useState(null);
  const width = 320;
  const height = 170;
  const padding = { top: 18, right: 16, bottom: 28, left: 42 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const series = [
    { key: 'pangyo', label: '판교', color: '#3676a9', rows: pangyoRows, visible: visibleAreas.includes('pangyo_1st_technovalley') },
    { key: 'wirye', label: '위례', color: '#d97b2b', rows: wiryeRows, visible: visibleAreas.includes('wirye_plan_area') },
  ].filter((item) => item.visible);

  const allRows = series.flatMap((item) => item.rows);
  const maxValue = Math.max(1, ...allRows.map((row) => Number(row[valueKey]) || 0));
  const ticks = [0, 10, 20, 30, 40, 50, 60];

  function xScale(timeMin) {
    return padding.left + (Number(timeMin) / 60) * chartWidth;
  }

  function yScale(value) {
    const ratio = (Number(value) || 0) / maxValue;
    return padding.top + chartHeight - ratio * chartHeight;
  }

  function buildPath(rowsForSeries) {
    return rowsForSeries
      .map((row, index) => `${index === 0 ? 'M' : 'L'} ${xScale(row.timeMin)} ${yScale(row[valueKey])}`)
      .join(' ');
  }

  function showTooltip(event, areaLabel, row) {
    const { x, y } = getChartTooltipPosition(event, 220, 120);
    setTooltip({
      visible: true,
      x,
      y,
      title: areaLabel,
      rows: [
        { label: '이동시간', value: `${row.timeMin}분` },
        {
          label: valueKey === 'reachableWorkers' ? '도달 가능 종사자' : '도달 가능 인구',
          value: formatWholePeople(row[valueKey]),
        },
      ],
    });
  }

  return (
    <div className="line-chart-card">
      <strong>{title}</strong>
      <div className="line-chart-frame">
        <ChartHoverTooltip tooltip={tooltip} />
        <svg className="line-chart-svg" viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
          <line className="line-axis" x1={padding.left} y1={padding.top} x2={padding.left} y2={padding.top + chartHeight} />
          <line className="line-axis" x1={padding.left} y1={padding.top + chartHeight} x2={padding.left + chartWidth} y2={padding.top + chartHeight} />
          {[0, 0.25, 0.5, 0.75, 1].map((tick, index) => {
            const value = maxValue * tick;
            const y = yScale(value);
            return (
              <g key={`${title}-y-${index}`}>
                <line className="line-grid" x1={padding.left} y1={y} x2={padding.left + chartWidth} y2={y} />
                <text className="line-axis-label" x={padding.left - 8} y={y + 4} textAnchor="end">
                  {tick === 0 ? '0' : `${Math.round(value / 10000).toLocaleString('ko-KR')}만`}
                </text>
              </g>
            );
          })}
          {ticks.map((tick) => (
            <g key={`${title}-x-${tick}`}>
              <line className="line-grid tick" x1={xScale(tick)} y1={padding.top + chartHeight} x2={xScale(tick)} y2={padding.top + chartHeight + 4} />
              <text className="line-axis-label" x={xScale(tick)} y={padding.top + chartHeight + 18} textAnchor="middle">
                {tick}
              </text>
            </g>
          ))}
          {series.map((item) => (
            <g key={`${title}-${item.key}`}>
              <path className="line-series-path" d={buildPath(item.rows)} stroke={item.color} />
              {item.rows.map((row) => (
                <circle
                  className="line-series-point"
                  cx={xScale(row.timeMin)}
                  cy={yScale(row[valueKey])}
                  fill={item.color}
                  key={`${title}-${item.key}-${row.timeMin}`}
                  onMouseEnter={(event) => showTooltip(event, item.label, row)}
                  onMouseMove={(event) => showTooltip(event, item.label, row)}
                  onMouseLeave={() => setTooltip(null)}
                  r="4"
                />
              ))}
            </g>
          ))}
          <text className="line-axis-title" x={padding.left} y={14}>
            {unitLabel}
          </text>
        </svg>
      </div>
    </div>
  );
}

function CompositionSection({
  areas,
  categoryKey,
  rows,
  title,
  description,
  ratioKey = 'area_ratio',
  valueKey = 'area_sqm',
  valueFormatter = formatSqm,
  showChip = true,
  rowBuilder = topCompositionRows,
}) {
  const showValue = Boolean(valueKey);
  const safeAreas = Array.isArray(areas) ? areas : [];
  const safeRows = Array.isArray(rows) ? rows : [];

  return (
    <div className="placeholder-card composition-card">
      <span>{title}</span>
      {description ? <p className="composition-description">{description}</p> : null}
      <div className={safeAreas.length > 1 ? 'composition-columns' : 'composition-columns single'}>
        {safeAreas.map((areaName) => (
          <div className="composition-column" key={areaName}>
            <strong>{areaLabels[areaName]}</strong>
            {rowBuilder(safeRows, areaName, categoryKey, ratioKey, valueKey).map((row) => {
              const displayCategory = categoryKey === 'main_use' ? getDevelopmentMainUseLabel(row.category) : row.category;

              return (
                <div className="composition-row" key={`${areaName}-${row.category}`}>
                  <span className="composition-left">
                    {showChip ? <i style={{ backgroundColor: getCategoryChipColor(row.category, categoryKey) }} /> : null}
                    <span title={displayCategory}>{displayCategory}</span>
                  </span>
                  <small className="composition-sub">
                    {showValue && row.value ? `${formatPercent(row.ratio)} · ${valueFormatter(row.value)}` : formatPercent(row.ratio)}
                  </small>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

const Root = window.location.pathname === '/boundary-editor' ? BoundaryEditor : App;

createRoot(document.getElementById('root')).render(<Root />);



