import React, { useEffect, useMemo, useState } from 'react';
import DeckGL from '@deck.gl/react';
import { BitmapLayer, GeoJsonLayer, ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import { TileLayer } from '@deck.gl/geo-layers';
import proj4 from 'proj4';
import pangyoCandidateParcelsRaw from '../../analysis_boundaries/pangyo_1st_technovalley_candidate_parcels_5186.geojson?raw';
import wiryeCandidateParcelsRaw from '../../analysis_boundaries/wirye_business_commercial_candidate_parcels_5186.geojson?raw';

const dataUrl = (path) => `${import.meta.env.BASE_URL}${String(path).replace(/^\/+/, '')}`;

export const MAP_VIEWS = {
  pangyo: {
    longitude: 127.111,
    latitude: 37.394,
    zoom: 13.5,
    pitch: 0,
    bearing: 0,
  },
  wirye: {
    longitude: 127.14,
    latitude: 37.462,
    zoom: 13.2,
    pitch: 0,
    bearing: 0,
  },
  comparison: {
    longitude: 127.126,
    latitude: 37.428,
    zoom: 11.2,
    pitch: 0,
    bearing: 0,
  },
};

const VWORLD_TILE_SIZE = 256;
const EPSG_5186 = '+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=600000 +ellps=GRS80 +units=m +no_defs';
const EPSG_4326 = 'EPSG:4326';

const AREA_STYLES = {
  pangyo_1st_technovalley: {
    stroke: [34, 104, 166, 230],
    fill: [34, 104, 166, 42],
  },
  wirye_plan_area: {
    stroke: [219, 123, 43, 230],
    fill: [219, 123, 43, 42],
  },
};

const STATION_COLOR = [22, 31, 44, 245];
const LANDUSE_BOUNDARY_LINE = [24, 28, 33, 238];
const DEVELOPMENT_BOUNDARY_LINE = [24, 28, 33, 238];
const DEVELOPMENT_BUILDING_FILL = [145, 170, 190, 92];
const DEVELOPMENT_OFFICE_FILL = [49, 102, 164, 185];
const DEVELOPMENT_OFFICE_LINE = [33, 77, 125, 210];
const DEVELOPMENT_VACANT_FILL = [228, 198, 129, 92];
const DEVELOPMENT_VACANT_LINE = [141, 111, 60, 200];
const DEVELOPMENT_USE_OTHER = [176, 184, 193];
const ACCESS_30_FILL = [41, 97, 164, 128];
const ACCESS_30_LINE = [32, 74, 126, 230];
const ACCESS_60_FILL = [122, 164, 214, 76];
const ACCESS_60_LINE = [76, 113, 158, 210];
const STATION_500_FILL = [235, 137, 52, 44];
const STATION_500_LINE = [202, 102, 24, 215];
const STATION_1000_FILL = [246, 176, 92, 24];
const STATION_1000_LINE = [221, 142, 54, 176];
export const DEVELOPMENT_MAIN_USE_LEGEND = [
  { label: '업무시설', color: [49, 102, 164] },
  { label: '교육연구시설', color: [239, 190, 63] },
  { label: '공동주택', color: [96, 168, 116] },
  { label: '자동차관련시설', color: [168, 153, 124] },
  { label: '제1종근린생활시설', color: [226, 164, 86] },
  { label: '제2종근린생활시설', color: [219, 129, 72] },
  { label: '단독주택', color: [122, 171, 141] },
  { label: '판매시설', color: [198, 83, 105] },
  { label: '공장', color: [117, 102, 172] },
  { label: '기타', color: DEVELOPMENT_USE_OTHER },
];

const JOBS_NO_DATA_FILL = [201, 208, 216, 120];
const JOBS_LOW_FILL = [224, 236, 247, 196];
const JOBS_HIGH_FILL = [17, 79, 147, 232];
const JOBS_BALANCE_COLORS = {
  employment: [64, 122, 197, 210],
  residential: [229, 146, 79, 210],
  mixed: [132, 111, 171, 198],
  no_data: [201, 208, 216, 120],
};

export const LANDUSE_ZONE_LEGEND = [
  { label: '준주거지역', color: [238, 194, 69] },
  { label: '자연녹지지역', color: [64, 154, 88] },
  { label: '보전녹지지역', color: [126, 194, 94] },
  { label: '제1종전용주거지역', color: [38, 126, 72] },
  { label: '제1종일반주거지역', color: [96, 176, 122] },
  { label: '제2종일반주거지역', color: [151, 164, 176] },
  { label: '제2종일반주거지역(7층이하)', color: [236, 139, 72] },
  { label: '제2종일반주거지역(7층)', color: [243, 169, 88] },
  { label: '제3종일반주거지역', color: [247, 185, 103] },
  { label: '일반상업지역', color: [250, 197, 116] },
  { label: '근린상업지역', color: [248, 203, 120] },
  { label: '중심상업지역', color: [250, 218, 148] },
  { label: '개발제한구역', color: [202, 78, 97] },
  { label: '기타 도시지역', color: [167, 79, 143] },
  { label: '장지 도시자연공원구역', color: [219, 108, 86] },
  { label: '기타', color: [117, 102, 172] },
];

export const BLOCK_TYPE_LEGEND = [
  { label: '도시지원시설용지', color: [54, 118, 169] },
  { label: '도로', color: [125, 137, 148] },
  { label: '하천', color: [64, 146, 195] },
  { label: '어린이공원', color: [96, 168, 116] },
  { label: '보행자전용도로', color: [168, 153, 124] },
  { label: '주차장', color: [229, 174, 83] },
  { label: '공공공지', color: [198, 83, 105] },
  { label: '일반광장', color: [118, 91, 164] },
  { label: '완충녹지', color: [150, 125, 184] },
  { label: '근린공원', color: [125, 144, 178] },
  { label: '수도공급시설', color: [150, 125, 184] },
  { label: '경관녹지', color: [202, 78, 97] },
  { label: '기타', color: [176, 184, 193] },
];

const LANDUSE_ZONE_COLORS = Object.fromEntries(
  LANDUSE_ZONE_LEGEND.map((item) => [item.label, [...item.color, 160]]),
);

const BLOCK_TYPE_COLORS = {
  '도시지원시설용지': [54, 118, 169, 220],
  '도로': [125, 137, 148, 210],
  '하천': [64, 146, 195, 220],
  '어린이공원': [96, 168, 116, 220],
  '보행자전용도로': [168, 153, 124, 220],
  '주차장': [229, 174, 83, 220],
  '공공공지': [198, 83, 105, 220],
  '일반광장': [118, 91, 164, 220],
  '완충녹지': [150, 125, 184, 220],
  '근린공원': [125, 144, 178, 220],
  '수도공급시설': [150, 125, 184, 220],
  '경관녹지': [202, 78, 97, 220],
  '기타': [176, 184, 193, 220],
};

const DEVELOPMENT_CANDIDATE_PARCELS = {
  pangyo: transformFeatureCollection(JSON.parse(pangyoCandidateParcelsRaw)),
  wirye: transformFeatureCollection(JSON.parse(wiryeCandidateParcelsRaw)),
};

const FALLBACK_COLORS = [
  [49, 130, 189, 112],
  [230, 126, 34, 112],
  [46, 160, 90, 112],
  [155, 89, 182, 112],
  [196, 92, 92, 112],
  [80, 150, 150, 112],
  [155, 137, 68, 112],
  [99, 110, 180, 112],
];

function transformPosition(position) {
  if (!Array.isArray(position) || position.length < 2) {
    return position;
  }

  const [x, y, z] = position;
  const [longitude, latitude] = proj4(EPSG_5186, EPSG_4326, [x, y]);
  return z === undefined ? [longitude, latitude] : [longitude, latitude, z];
}

function transformCoordinates(coordinates) {
  if (!Array.isArray(coordinates)) {
    return coordinates;
  }

  if (typeof coordinates[0] === 'number') {
    return transformPosition(coordinates);
  }

  return coordinates.map(transformCoordinates);
}

function transformFeature(feature) {
  return {
    ...feature,
    geometry: {
      ...feature.geometry,
      coordinates: transformCoordinates(feature.geometry.coordinates),
    },
  };
}

function transformFeatureCollection(collection) {
  return {
    ...collection,
    features: collection.features.map(transformFeature),
  };
}

function getFirstCoordinate(coordinates) {
  if (!Array.isArray(coordinates)) {
    return null;
  }

  if (typeof coordinates[0] === 'number' && typeof coordinates[1] === 'number') {
    return coordinates;
  }

  for (const child of coordinates) {
    const found = getFirstCoordinate(child);
    if (found) {
      return found;
    }
  }

  return null;
}

function normalizeFeatureCollectionCoordinates(collection) {
  if (!collection?.features?.length) {
    return emptyFeatureCollection();
  }

  const firstFeature = collection.features.find((feature) => feature?.geometry?.coordinates);
  const firstCoordinate = firstFeature ? getFirstCoordinate(firstFeature.geometry.coordinates) : null;

  if (!firstCoordinate) {
    return collection;
  }

  const [x, y] = firstCoordinate;
  const looksProjected = Math.abs(Number(x)) > 180 || Math.abs(Number(y)) > 90;

  return looksProjected ? transformFeatureCollection(collection) : collection;
}

function filterByScope(collection, scope) {
  if (!collection || scope === 'comparison') {
    return collection;
  }

  const areaName = scope === 'pangyo' ? 'pangyo_1st_technovalley' : 'wirye_plan_area';
  return {
    ...collection,
    features: collection.features.filter((feature) => feature.properties?.area_name === areaName),
  };
}

function hashCategory(category) {
  return String(category ?? '')
    .split('')
    .reduce((sum, char) => sum + char.charCodeAt(0), 0);
}

function formatArea(areaSqm) {
  if (!Number.isFinite(Number(areaSqm))) {
    return null;
  }

  return `${Number(areaSqm).toLocaleString('ko-KR', { maximumFractionDigits: 0 })}㎡`;
}

function formatHectare(areaHa) {
  if (!Number.isFinite(Number(areaHa))) {
    return null;
  }

  return `${Number(areaHa).toLocaleString('ko-KR', { maximumFractionDigits: 2 })}ha`;
}

function getAreaLabel(areaName) {
  if (areaName === 'pangyo_1st_technovalley') {
    return '판교';
  }

  if (areaName === 'wirye_plan_area') {
    return '위례';
  }

  return areaName || null;
}

function tooltipRows(rows) {
  return rows
    .filter(([, value]) => value !== undefined && value !== null && value !== '' && value !== '-')
    .map(([label, value]) => `<div>${label}: ${value}</div>`)
    .join('');
}

function getAreaStyle(feature, type) {
  const areaName = feature.properties?.area_name;
  const style = AREA_STYLES[areaName] ?? AREA_STYLES.pangyo_1st_technovalley;
  return type === 'fill' ? style.fill : style.stroke;
}

function getCategoryColor(category, colorMap) {
  if (colorMap[category]) {
    return colorMap[category];
  }

  return FALLBACK_COLORS[hashCategory(category) % FALLBACK_COLORS.length];
}

function getLanduseLineColor(color) {
  return [color[0], color[1], color[2], 225];
}

const DEVELOPMENT_MAIN_USE_LABELS = DEVELOPMENT_MAIN_USE_LEGEND.map((item) => item.label);
const DEVELOPMENT_MAIN_USE_SET = new Set(DEVELOPMENT_MAIN_USE_LABELS);
const DEVELOPMENT_MAIN_USE_MAP = Object.fromEntries(
  DEVELOPMENT_MAIN_USE_LEGEND.map((item) => [item.label, item.color]),
);

export function normalizeDevelopmentMainUse(value) {
  const raw = String(value ?? '').trim();
  if (!raw) return '기타';

  const normalized = raw.replace(/[\s()[\]{}.,·\/_-]/g, '');
  const aliases = {
    기타: '기타',
    기타미분류: '기타',
    미분류: '기타',
    '기타/미분류': '기타',
  };

  const alias = aliases[normalized];
  if (alias) return alias;

  const matched = DEVELOPMENT_MAIN_USE_LABELS.find((label) => label.replace(/[\s()[\]{}.,·\/_-]/g, '') === normalized);
  return matched ?? '기타';
}

export function getDevelopmentMainUseColor(mainUse) {
  const normalized = normalizeDevelopmentMainUse(mainUse);
  const rgb = DEVELOPMENT_MAIN_USE_MAP[normalized] ?? DEVELOPMENT_MAIN_USE_MAP.기타;
  return [...rgb, 180];
}

export function getDevelopmentMainUseLabel(mainUse) {
  return normalizeDevelopmentMainUse(mainUse);
}

function getDevelopmentLegendItems(collection, scope) {
  const scoped = filterByScope(collection, scope);
  const features = Array.isArray(scoped?.features) ? scoped.features : [];
  const usedLabels = new Set();

  features.forEach((feature) => {
    const label = getDevelopmentMainUseLabel(feature?.properties?.main_use);
    usedLabels.add(label);
  });

  const items = DEVELOPMENT_MAIN_USE_LEGEND.filter((item) => usedLabels.has(item.label));
  return items.length ? items : DEVELOPMENT_MAIN_USE_LEGEND.filter((item) => item.label === '기타');
}

function getDevelopmentAreaCollection(scope) {
  if (scope === 'pangyo') {
    return DEVELOPMENT_CANDIDATE_PARCELS.pangyo;
  }

  if (scope === 'wirye') {
    return DEVELOPMENT_CANDIDATE_PARCELS.wirye;
  }

  return null;
}

function getJobsMetricConfig(metric) {
  const configs = {
    jobs_balance: { label: '직주균형', unit: null },
    population_allocated: { label: '인구', unit: '명' },
    households_allocated: { label: '가구', unit: '가구' },
    business_count_allocated: { label: '사업체 수', unit: '개' },
    worker_count_allocated: { label: '종사자 수', unit: '명' },
  };

  return configs[metric] ?? configs.worker_count_allocated;
}

function formatJobsMetricValue(value, unit) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return null;
  }

  return `${number.toLocaleString('ko-KR', { minimumFractionDigits: 3, maximumFractionDigits: 3 })}${unit}`;
}

function mixColor(low, high, ratio) {
  const clamped = Math.max(0, Math.min(1, ratio));
  return low.map((channel, index) => {
    const next = high[index] ?? channel;
    return Math.round(channel + (next - channel) * clamped);
  });
}

function getJobsMetricColor(value, range) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return JOBS_NO_DATA_FILL;
  }

  const min = Number(range?.min);
  const max = Number(range?.max);
  const span = Number.isFinite(min) && Number.isFinite(max) ? max - min : 0;
  const normalized = span > 0 ? (number - min) / span : 1;
  const ratio = Math.sqrt(Math.max(0, normalized));
  return mixColor(JOBS_LOW_FILL, JOBS_HIGH_FILL, ratio);
}

function getJobsBalanceType(properties) {
  const population = Number(properties?.population_allocated);
  const workers = Number(properties?.worker_count_allocated);

  if (!Number.isFinite(population) || !Number.isFinite(workers)) {
    return 'no_data';
  }

  if (workers > population * 1.2) {
    return 'employment';
  }

  if (population > workers * 1.2) {
    return 'residential';
  }

  return 'mixed';
}

function getJobsBalanceLabel(type) {
  const labels = {
    employment: '고용 우세',
    residential: '주거 우세',
    mixed: '혼합형',
    no_data: '데이터 없음',
  };

  return labels[type] ?? labels.no_data;
}

function formatJobsBalanceRatio(properties) {
  const population = Number(properties?.population_allocated);
  const workers = Number(properties?.worker_count_allocated);

  if (!Number.isFinite(population) || !Number.isFinite(workers) || population <= 0) {
    return null;
  }

  return (workers / population).toLocaleString('ko-KR', {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  });
}

function getJobsMetricRange(collection, metric, scope) {
  if (metric === 'jobs_balance') {
    return null;
  }
  const scoped = filterByScope(collection, scope);
  const values = scoped?.features
    ?.map((feature) => Number(feature.properties?.[metric]))
    .filter((value) => Number.isFinite(value));

  if (!values?.length) {
    return null;
  }

  return { min: Math.min(...values), max: Math.max(...values) };
}

function makeTooltip({ object, layer }) {
  if (!object || !layer) {
    return null;
  }

  const properties = object.properties ?? object;

  if (layer.id.includes('boundary')) {
    return {
      html: `<div class="map-tooltip-title">${properties.display_name ?? properties.name ?? '분석경계'}</div>
        ${tooltipRows([
          ['레이어', '분석경계'],
          ['면적', formatArea(properties.area_sqm)],
          ['출처/방식', properties.boundary_method ?? properties.source],
        ])}`,
    };
  }

  if (layer.id.includes('landuse-zone')) {
    return {
      html: `<div class="map-tooltip-title">${properties.landuse_category ?? '용도지역'}</div>
        ${tooltipRows([
          ['지역명', getAreaLabel(properties.area_name)],
          ['레이어', '용도지역'],
          ['면적', formatArea(properties.area_sqm)],
          ['면적(ha)', formatHectare(properties.area_ha)],
        ])}`,
    };
  }

  if (layer.id.includes('landuse-missing')) {
    return {
      html: `<div class="map-tooltip-title">데이터 없음</div>
        ${tooltipRows([
          ['지역명', getAreaLabel(properties.area_name)],
          ['레이어', '용도지역 결측'],
          ['면적', formatArea(properties.area_sqm)],
        ])}`,
    };
  }

  if (layer.id.includes('landuse-blocktype')) {
    return {
      html: `<div class="map-tooltip-title">${properties.blockType ?? 'blockType'}</div>
        ${tooltipRows([
          ['지역명', getAreaLabel(properties.area_name)],
          ['레이어', 'blockType'],
          ['면적', formatArea(properties.area_sqm)],
          ['면적(ha)', formatHectare(properties.area_ha)],
        ])}`,
    };
  }

  if (layer.id.includes('development-building')) {
    const areaLabel = getAreaLabel(properties.area_name) ?? (layer.id.includes('pangyo') ? '판교' : '위례');
    const rawMainUse = String(properties.main_use ?? '').trim() || '기타';
    const officeFlag = rawMainUse.includes('업무시설') ? '예' : '아니오';

    return {
      html: `<div class="map-tooltip-title">${rawMainUse}</div>
        ${tooltipRows([
          ['지역명', areaLabel],
          ['객체 유형', '건축물/필지'],
          ['주용도', rawMainUse],
          ['연면적', formatArea(properties.total_floor_area_sqm)],
          ['건축면적', formatArea(properties.building_area_sqm)],
          ['건폐율', Number.isFinite(Number(properties.bcr)) ? `${Number(properties.bcr).toLocaleString('ko-KR', { maximumFractionDigits: 2 })}%` : null],
          ['용적률', Number.isFinite(Number(properties.far)) ? `${Number(properties.far).toLocaleString('ko-KR', { maximumFractionDigits: 2 })}%` : null],
          ['승인연도', properties.approval_year],
          ['사용승인일', properties.approval_date ? String(properties.approval_date).slice(0, 10) : null],
          ['업무시설 여부', officeFlag],
        ])}`,
    };
  }

  if (layer.id.includes('development-vacant')) {
    const areaLabel = getAreaLabel(properties.area_name) ?? (layer.id.includes('pangyo') ? '판교' : '위례');

    return {
      html: `<div class="map-tooltip-title">${properties.analysis_category ?? properties.blockType ?? '미건축·공지 추정'}</div>
        ${tooltipRows([
          ['지역명', areaLabel],
          ['객체 유형', '미건축·공지 추정'],
          ['구역명', properties.zoneName],
          ['블록명', properties.blockName],
          ['필지명', properties.lotName],
          ['필지 ID', properties.parcel_id],
          ['면적', formatArea(properties.area_sqm)],
        ])}`,
    };
  }

  if (layer.id.includes('jobs-census')) {
    const metric = layer.id.split('-')[2] ?? 'worker_count_allocated';
    const metricConfig = getJobsMetricConfig(metric);
    const balanceType = getJobsBalanceType(properties);

    return {
      html: `<div class="map-tooltip-title">${getAreaLabel(properties.area_name) ?? '집계구'}</div>
        ${tooltipRows([
          ['지역', getAreaLabel(properties.area_name)],
          ...(metric === 'jobs_balance'
            ? [
                ['직주균형 유형', getJobsBalanceLabel(balanceType)],
                ['workers / population', formatJobsBalanceRatio(properties)],
              ]
            : [
                ['선택 지표', metricConfig.label],
                ['값', formatJobsMetricValue(properties[metric], metricConfig.unit)],
              ]),
          ['인구', formatJobsMetricValue(properties.population_allocated, '명')],
          ['가구', formatJobsMetricValue(properties.households_allocated, '가구')],
          ['사업체 수', formatJobsMetricValue(properties.business_count_allocated, '개')],
          ['종사자 수', formatJobsMetricValue(properties.worker_count_allocated, '명')],
        ])}`,
    };
  }

  if (layer.id.includes('accessibility-iso')) {
    const threshold = Number(properties.time_threshold_min);
    return {
      html: `<div class="map-tooltip-title">${getAreaLabel(properties.area_name) ?? '등시간권'}</div>
        ${tooltipRows([
          ['시간대', Number.isFinite(threshold) ? `${threshold}분 이내` : null],
          ['도달 가능 인구', formatJobsMetricValue(properties.reachable_population, '명')],
          ['도달 가능 종사자', formatJobsMetricValue(properties.reachable_workers, '명')],
        ])}`,
    };
  }

  if (layer.id.includes('station-buffer')) {
    const radius = Number(properties.buffer_m);
    const ratio = Number(properties.buffer_area_ratio);
    return {
      html: `<div class="map-tooltip-title">${getAreaLabel(properties.area_name) ?? '역세권'}</div>
        ${tooltipRows([
          ['기준역', properties.station_name],
          ['반경', Number.isFinite(radius) ? `${radius}m` : null],
          ['분석구역 내 면적 비율', Number.isFinite(ratio) ? `${(ratio * 100).toLocaleString('ko-KR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%` : null],
        ])}`,
    };
  }

  if (layer.id.includes('station')) {
    const areaLabel =
      properties.area_name === 'pangyo_1st_technovalley'
        ? '판교 제1테크노밸리'
        : properties.area_name === 'wirye_plan_area'
          ? '위례 계획구역'
          : properties.area_name;

    return {
      html: `<div class="map-tooltip-title">${properties.station_name ?? '핵심역'}</div>
        ${tooltipRows([
          ['지역', areaLabel],
          ['역명', properties.station_name],
          ['노선명', properties.line_name],
          ['역 역할', properties.station_role],
        ])}`,
    };
  }

  return null;
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status}`);
  }
  const json = await response.json();
  return json?.type === 'FeatureCollection' ? normalizeFeatureCollectionCoordinates(json) : json;
}

function emptyFeatureCollection() {
  return { type: 'FeatureCollection', features: [] };
}

function createBaseMapLayer({ apiKey, tileFailed, setTileFailed, id }) {
  if (!apiKey) {
    return null;
  }

  return new TileLayer({
    id,
    data: `https://api.vworld.kr/req/wmts/1.0.0/${apiKey}/Base/{z}/{y}/{x}.png`,
    minZoom: 0,
    maxZoom: 18,
    tileSize: VWORLD_TILE_SIZE,
    renderSubLayers: (props) => {
      const {
        bbox: { west, south, east, north },
      } = props.tile;

      return new BitmapLayer(props, {
        data: null,
        image: props.data,
        bounds: [west, south, east, north],
      });
    },
    onTileError: () => {
      if (!tileFailed) {
        setTileFailed(true);
      }
    },
  });
}

function createOverlayLayers({ boundaries, stations, scope, subduedBoundary = false }) {
  const scopedBoundaries = filterByScope(boundaries, scope);
  const scopedStations = filterByScope(stations, scope);
  const boundaryColor = subduedBoundary ? [24, 28, 33, 238] : [24, 28, 33, 238];

  return [
    scopedBoundaries &&
      new GeoJsonLayer({
        id: `overlay-boundary-${scope}`,
        data: scopedBoundaries,
        pickable: true,
        stroked: true,
        filled: false,
        getLineColor: boundaryColor,
        getLineWidth: subduedBoundary ? 2.4 : 2.6,
        lineWidthUnits: 'pixels',
      }),
    scopedStations &&
      new ScatterplotLayer({
        id: `overlay-stations-${scope}`,
        data: scopedStations.features ?? [],
        pickable: true,
        getPosition: (feature) => feature.geometry?.coordinates ?? [0, 0],
        getRadius: 42,
        radiusUnits: 'pixels',
        radiusMinPixels: 6,
        radiusMaxPixels: 10,
        getFillColor: STATION_COLOR,
        getLineColor: [255, 255, 255, 230],
        lineWidthUnits: 'pixels',
        getLineWidth: 1.2,
        stroked: true,
      }),
    scopedStations &&
      new TextLayer({
        id: `overlay-station-labels-${scope}`,
        data: scopedStations.features ?? [],
        pickable: false,
        getPosition: (feature) => feature.geometry?.coordinates ?? [0, 0],
        getText: (feature) => feature.properties?.station_name ?? '',
        getColor: [26, 31, 37, 230],
        getSize: 12,
        getPixelOffset: [0, 16],
        sizeUnits: 'pixels',
        getTextAnchor: 'middle',
        getAlignmentBaseline: 'top',
        fontFamily: 'Pretendard, sans-serif',
      }),
  ].filter(Boolean);
}

function createLanduseLayers({ boundaries, zones, missing, blockTypes, scope, visibility }) {
  const scopedBoundaries = filterByScope(boundaries, scope);
  const scopedZones = filterByScope(zones, scope);
  const scopedMissing = filterByScope(missing, scope);
  const scopedBlockTypes = filterByScope(blockTypes, scope);

  return [
    visibility.zoning &&
      scopedMissing &&
      new GeoJsonLayer({
        id: `landuse-missing-${scope}`,
        data: scopedMissing,
        pickable: true,
        stroked: true,
        filled: true,
        getFillColor: [235, 239, 243, 138],
        getLineColor: [178, 186, 194, 150],
        getLineWidth: 0.55,
        lineWidthUnits: 'pixels',
      }),
    visibility.zoning &&
      scopedZones &&
      new GeoJsonLayer({
        id: `landuse-zone-${scope}`,
        data: scopedZones,
        pickable: true,
        stroked: true,
        filled: true,
        getFillColor: (feature) => getCategoryColor(feature.properties?.landuse_category ?? '기타', LANDUSE_ZONE_COLORS),
        getLineColor: (feature) => getLanduseLineColor(getCategoryColor(feature.properties?.landuse_category ?? '기타', LANDUSE_ZONE_COLORS)),
        getLineWidth: 0.7,
        lineWidthUnits: 'pixels',
        autoHighlight: true,
        highlightColor: [255, 255, 255, 96],
      }),
    visibility.blockType &&
      scopedBlockTypes &&
      new GeoJsonLayer({
        id: `landuse-blocktype-${scope}`,
        data: scopedBlockTypes,
        pickable: true,
        stroked: true,
        filled: false,
        getLineColor: [88, 96, 105, 180],
        getLineWidth: 0.8,
        lineWidthUnits: 'pixels',
        autoHighlight: true,
        highlightColor: [255, 255, 255, 90],
      }),
    scopedBoundaries &&
      new GeoJsonLayer({
        id: `landuse-boundary-${scope}`,
        data: scopedBoundaries,
        pickable: true,
        stroked: true,
        filled: false,
        getLineColor: LANDUSE_BOUNDARY_LINE,
        getLineWidth: 2.6,
        lineWidthUnits: 'pixels',
      }),
  ].filter(Boolean);
}

function useDashboardMapData() {
  const [state, setState] = useState({
    boundaries: emptyFeatureCollection(),
    stations: emptyFeatureCollection(),
    failed: false,
  });

  useEffect(() => {
    let ignore = false;

    async function load() {
      try {
        const [boundaries, stations] = await Promise.all([
          fetchJson(dataUrl('data/boundaries.geojson')),
          fetchJson(dataUrl('data/core_stations.geojson')),
        ]);

        if (!ignore) {
          setState({
            boundaries: boundaries?.features ? boundaries : emptyFeatureCollection(),
            stations: stations?.features ? stations : emptyFeatureCollection(),
            failed: false,
          });
        }
      } catch {
        if (!ignore) {
          setState((current) => ({ ...current, failed: true }));
        }
      }
    }

    load();
    return () => {
      ignore = true;
    };
  }, []);

  return state;
}

function useLanduseMapData(enabled) {
  const [state, setState] = useState({
    zones: emptyFeatureCollection(),
    missing: emptyFeatureCollection(),
    blockTypes: emptyFeatureCollection(),
    failed: false,
  });

  useEffect(() => {
    if (!enabled) return undefined;
    let ignore = false;

    async function load() {
      try {
        const [zones, blockTypes, missing] = await Promise.all([
          fetchJson(dataUrl('data/landuse_zones.geojson')),
          fetchJson(dataUrl('data/landuse_blocktype.geojson')),
          fetchJson(dataUrl('data/landuse_zones_missing.geojson')),
        ]);

        if (!ignore) {
          setState({
            zones: zones?.features ? zones : emptyFeatureCollection(),
            missing: missing?.features ? missing : emptyFeatureCollection(),
            blockTypes: blockTypes?.features ? blockTypes : emptyFeatureCollection(),
            failed: false,
          });
        }
      } catch {
        if (!ignore) {
          setState((current) => ({ ...current, failed: true }));
        }
      }
    }

    load();
    return () => {
      ignore = true;
    };
  }, [enabled]);

  return state;
}

function useDevelopmentMapData(enabled) {
  const [state, setState] = useState({
    buildings: emptyFeatureCollection(),
    failed: false,
  });

  useEffect(() => {
    if (!enabled) return undefined;
    let ignore = false;

    async function load() {
      try {
        const buildings = await fetchJson(dataUrl('data/buildings_or_parcels.geojson'));
        if (!ignore) {
          setState({
            buildings: buildings?.features ? buildings : emptyFeatureCollection(),
            failed: false,
          });
        }
      } catch {
        if (!ignore) {
          setState((current) => ({ ...current, failed: true }));
        }
      }
    }

    load();
    return () => {
      ignore = true;
    };
  }, [enabled]);

  return state;
}

function useJobsMapData(enabled) {
  const [state, setState] = useState({
    census: emptyFeatureCollection(),
    failed: false,
  });

  useEffect(() => {
    if (!enabled) return undefined;
    let ignore = false;

    async function load() {
      try {
        const census = await fetchJson(dataUrl('data/sgis_census.geojson'));
        if (!ignore) {
          setState({
            census: census?.features ? census : emptyFeatureCollection(),
            failed: false,
          });
        }
      } catch {
        if (!ignore) {
          setState((current) => ({ ...current, failed: true }));
        }
      }
    }

    load();
    return () => {
      ignore = true;
    };
  }, [enabled]);

  return state;
}

function useAccessibilityMapData(enabled) {
  const [state, setState] = useState({
    isochrones: emptyFeatureCollection(),
    stationBuffers: emptyFeatureCollection(),
    failed: false,
  });

  useEffect(() => {
    if (!enabled) return undefined;
    let ignore = false;

    async function load() {
      try {
        const [isochrones, stationBuffers, summaryText, stationAreaText] = await Promise.all([
          fetchJson(dataUrl('data/accessibility_isochrones.geojson')),
          fetchJson(dataUrl('data/station_buffers.geojson')),
          fetch(dataUrl('data/accessibility_summary.csv')).then((response) => {
            if (!response.ok) {
              throw new Error(`Failed to fetch accessibility summary: ${response.status}`);
            }
            return response.text();
          }),
          fetch(dataUrl('data/station_area_ratio.csv')).then((response) => {
            if (!response.ok) {
              throw new Error(`Failed to fetch station area ratio: ${response.status}`);
            }
            return response.text();
          }),
        ]);

        const summaryRows = summaryText
          .trim()
          .split(/\r?\n/)
          .slice(1)
          .map((line) => line.split(','))
          .map((parts) => ({
            area_name: parts[0],
            time_threshold_min: parts[2],
            reachable_population: parts[4],
            reachable_workers: parts[5],
          }));

        const summaryMap = new Map(
          summaryRows.map((row) => [`${row.area_name}-${row.time_threshold_min}`, row]),
        );

        const stationAreaRows = stationAreaText
          .trim()
          .split(/\r?\n/)
          .slice(1)
          .map((line) => line.split(','))
          .map((parts) => ({
            area_name: parts[0],
            station_name: parts[1],
            buffer_500m_area_ratio: parts[5],
            buffer_1km_area_ratio: parts[7],
          }));

        const stationAreaMap = new Map(stationAreaRows.map((row) => [row.area_name, row]));

        const merged = {
          ...isochrones,
          features: (isochrones.features ?? []).map((feature) => {
            const key = `${feature.properties?.area_name}-${feature.properties?.time_threshold_min}`;
            const matched = summaryMap.get(key);
            return matched
              ? {
                  ...feature,
                  properties: {
                    ...feature.properties,
                    reachable_population: matched.reachable_population,
                    reachable_workers: matched.reachable_workers,
                  },
                }
              : feature;
          }),
        };

        const mergedBuffers = {
          ...stationBuffers,
          features: (stationBuffers.features ?? []).map((feature) => {
            const matched = stationAreaMap.get(feature.properties?.area_name);
            const bufferM = Number(feature.properties?.buffer_m);
            return {
              ...feature,
              properties: {
                ...feature.properties,
                station_name: matched?.station_name ?? feature.properties?.station_name,
                buffer_area_ratio:
                  bufferM === 500
                    ? matched?.buffer_500m_area_ratio
                    : bufferM === 1000
                      ? matched?.buffer_1km_area_ratio
                      : null,
              },
            };
          }),
        };

        if (!ignore) {
          setState({
            isochrones: merged?.features ? merged : emptyFeatureCollection(),
            stationBuffers: mergedBuffers?.features ? mergedBuffers : emptyFeatureCollection(),
            failed: false,
          });
        }
      } catch {
        if (!ignore) {
          setState((current) => ({ ...current, failed: true }));
        }
      }
    }

    load();
    return () => {
      ignore = true;
    };
  }, [enabled]);

  return state;
}

function createDevelopmentLayers({ boundaries, buildings, scope, visibility }) {
  const scopedBoundaries = filterByScope(boundaries, scope);
  const scopedBuildings = filterByScope(buildings, scope);
  const candidateParcels = getDevelopmentAreaCollection(scope);

  return [
    visibility.vacant &&
      candidateParcels &&
      new GeoJsonLayer({
        id: `development-vacant-${scope}`,
        data: candidateParcels,
        pickable: true,
        stroked: true,
        filled: true,
        getFillColor: DEVELOPMENT_VACANT_FILL,
        getLineColor: DEVELOPMENT_VACANT_LINE,
        getLineWidth: 0.95,
        lineWidthUnits: 'pixels',
        autoHighlight: true,
        highlightColor: [255, 255, 255, 120],
      }),
    visibility.buildingParcel &&
      scopedBuildings &&
      new GeoJsonLayer({
        id: `development-building-${scope}`,
        data: scopedBuildings,
        pickable: true,
        stroked: true,
        filled: true,
        getFillColor: (feature) => getDevelopmentMainUseColor(feature.properties?.main_use),
        getLineColor: [34, 38, 42, 215],
        getLineWidth: 0.75,
        lineWidthUnits: 'pixels',
        autoHighlight: true,
        highlightColor: [255, 255, 255, 95],
      }),
    scopedBoundaries &&
      new GeoJsonLayer({
        id: `development-boundary-${scope}`,
        data: scopedBoundaries,
        pickable: true,
        stroked: true,
        filled: false,
        getFillColor: [0, 0, 0, 0],
        getLineColor: DEVELOPMENT_BOUNDARY_LINE,
        getLineWidth: 2.6,
        lineWidthUnits: 'pixels',
        autoHighlight: true,
        highlightColor: [0, 0, 0, 45],
      }),
  ].filter(Boolean);
}

function createJobsLayers({ census, scope, visibility, metric, metricRange }) {
  const scopedCensus = filterByScope(census, scope);

  return [
    visibility.census &&
      scopedCensus &&
      new GeoJsonLayer({
        id: `jobs-census-${metric}-${scope}`,
        data: scopedCensus,
        pickable: true,
        stroked: true,
        filled: true,
        getFillColor: (feature) =>
          metric === 'jobs_balance'
            ? JOBS_BALANCE_COLORS[getJobsBalanceType(feature.properties)]
            : getJobsMetricColor(feature.properties?.[metric], metricRange),
        getLineColor: [248, 250, 252, 165],
        getLineWidth: 0.55,
        lineWidthUnits: 'pixels',
        autoHighlight: true,
        highlightColor: [255, 255, 255, 118],
      }),
  ].filter(Boolean);
}

function createAccessibilityLayers({ boundaries, stations, isochrones, scope, timeMode = 'all' }) {
  const scopedIsochrones = filterByScope(isochrones, scope);
  const features = Array.isArray(scopedIsochrones?.features) ? scopedIsochrones.features : [];
  const show30 = timeMode === '30' || timeMode === 'all';
  const show60 = timeMode === '60' || timeMode === 'all';
  const data60 = features.filter((feature) => Number(feature.properties?.time_threshold_min) === 60);
  const data30 = features.filter((feature) => Number(feature.properties?.time_threshold_min) === 30);

  return [
    show60 &&
      data60.length > 0 &&
      new GeoJsonLayer({
        id: `accessibility-iso-60-${scope}`,
        data: { type: 'FeatureCollection', features: data60 },
        pickable: true,
        stroked: true,
        filled: true,
        getFillColor: ACCESS_60_FILL,
        getLineColor: ACCESS_60_LINE,
        getLineWidth: 1.1,
        lineWidthUnits: 'pixels',
        autoHighlight: true,
        highlightColor: [255, 255, 255, 72],
      }),
    show30 &&
      data30.length > 0 &&
      new GeoJsonLayer({
        id: `accessibility-iso-30-${scope}`,
        data: { type: 'FeatureCollection', features: data30 },
        pickable: true,
        stroked: true,
        filled: true,
        getFillColor: ACCESS_30_FILL,
        getLineColor: ACCESS_30_LINE,
        getLineWidth: 1.2,
        lineWidthUnits: 'pixels',
        autoHighlight: true,
        highlightColor: [255, 255, 255, 88],
      }),
  ].filter(Boolean);
}

function createStationBufferLayers({ stationBuffers, scope, visibility }) {
  const scopedBuffers = filterByScope(stationBuffers, scope);
  const features = Array.isArray(scopedBuffers?.features) ? scopedBuffers.features : [];
  const data500 = features.filter((feature) => Number(feature.properties?.buffer_m) === 500);
  const data1000 = features.filter((feature) => Number(feature.properties?.buffer_m) === 1000);

  return [
    visibility.station1km &&
      data1000.length > 0 &&
      new GeoJsonLayer({
        id: `station-buffer-1000-${scope}`,
        data: { type: 'FeatureCollection', features: data1000 },
        pickable: true,
        stroked: true,
        filled: true,
        getFillColor: STATION_1000_FILL,
        getLineColor: STATION_1000_LINE,
        getLineWidth: 1,
        lineWidthUnits: 'pixels',
      }),
    visibility.station500m &&
      data500.length > 0 &&
      new GeoJsonLayer({
        id: `station-buffer-500-${scope}`,
        data: { type: 'FeatureCollection', features: data500 },
        pickable: true,
        stroked: true,
        filled: true,
        getFillColor: STATION_500_FILL,
        getLineColor: STATION_500_LINE,
        getLineWidth: 1.1,
        lineWidthUnits: 'pixels',
      }),
  ].filter(Boolean);
}

function createAccessibilityBoundaryAndStationLayers({ boundaries, stations, scope, visibility }) {
  const scopedBoundaries = filterByScope(boundaries, scope);
  const scopedStations = filterByScope(stations, scope);

  return [
    scopedBoundaries &&
      new GeoJsonLayer({
        id: `accessibility-boundary-${scope}`,
        data: scopedBoundaries,
        pickable: true,
        stroked: true,
        filled: false,
        getLineColor: [24, 28, 33, 238],
        getLineWidth: 2.6,
        lineWidthUnits: 'pixels',
      }),
    visibility.station &&
      scopedStations &&
      new ScatterplotLayer({
        id: `accessibility-stations-${scope}`,
        data: scopedStations.features ?? [],
        pickable: true,
        getPosition: (feature) => feature.geometry?.coordinates ?? [0, 0],
        getRadius: 42,
        radiusUnits: 'pixels',
        radiusMinPixels: 6,
        radiusMaxPixels: 10,
        getFillColor: STATION_COLOR,
        getLineColor: [255, 255, 255, 230],
        lineWidthUnits: 'pixels',
        getLineWidth: 1.2,
        stroked: true,
      }),
  ].filter(Boolean);
}

export function DashboardMap({
  initialView = 'comparison',
  overlayTitle,
  overlayDescription,
  analysisLayer = 'base',
  layerVisibility,
  jobsMetric = 'worker_count_allocated',
  accessibilityTimeMode = 'all',
  showDetailedLegend = true,
}) {
  const apiKey = import.meta.env.VITE_VWORLD_KEY;
  const [viewState, setViewState] = useState(MAP_VIEWS[initialView] ?? MAP_VIEWS.comparison);
  const [tileFailed, setTileFailed] = useState(false);
  const { boundaries, stations, failed: dataFailed } = useDashboardMapData();
  const { zones, missing, blockTypes, failed: landuseFailed } = useLanduseMapData(analysisLayer === 'landuse');
  const { buildings, failed: developmentFailed } = useDevelopmentMapData(analysisLayer === 'development');
  const { census, failed: jobsFailed } = useJobsMapData(analysisLayer === 'jobs');
  const { isochrones, stationBuffers, failed: accessibilityFailed } = useAccessibilityMapData(analysisLayer === 'accessibility');
  const visibility = {
    zoning: true,
    blockType: true,
    buildingParcel: true,
    vacant: true,
    census: true,
    station: true,
    ...layerVisibility,
  };
  const jobsMetricRange = useMemo(() => getJobsMetricRange(census, jobsMetric, initialView === 'pangyo' || initialView === 'wirye' ? initialView : 'comparison'), [census, initialView, jobsMetric]);
  const scope = initialView === 'pangyo' || initialView === 'wirye' ? initialView : 'comparison';
  const developmentLegendItems = useMemo(
    () => getDevelopmentLegendItems(buildings, scope),
    [buildings, scope],
  );

  const layers = useMemo(() => {
    const baseLayer = createBaseMapLayer({ apiKey, tileFailed, setTileFailed, id: `vworld-base-map-${scope}` });
    return [
      baseLayer,
      ...(analysisLayer === 'landuse'
        ? createLanduseLayers({ boundaries, zones, missing, blockTypes, scope, visibility })
        : analysisLayer === 'development'
          ? createDevelopmentLayers({ boundaries, buildings, scope, visibility })
          : analysisLayer === 'jobs'
            ? createJobsLayers({ census, scope, visibility, metric: jobsMetric, metricRange: jobsMetricRange })
            : analysisLayer === 'accessibility'
              ? createAccessibilityLayers({ boundaries, stations, isochrones, scope, timeMode: accessibilityTimeMode })
                  .concat(createStationBufferLayers({ stationBuffers, scope, visibility }))
                  .concat(createAccessibilityBoundaryAndStationLayers({ boundaries, stations, scope, visibility }))
          : []),
      ...createOverlayLayers({
        boundaries: analysisLayer === 'jobs' || analysisLayer === 'base' ? boundaries : null,
        stations: visibility.station && analysisLayer !== 'accessibility' ? stations : null,
        scope,
        subduedBoundary: analysisLayer !== 'base',
      }),
    ].filter(Boolean);
  }, [accessibilityTimeMode, analysisLayer, apiKey, blockTypes, boundaries, buildings, census, isochrones, jobsMetric, jobsMetricRange, layerVisibility, missing, scope, stationBuffers, stations, tileFailed, zones]);

  const failureMessage = !apiKey
    ? 'VWorld API 키가 설정되지 않았습니다.'
    : tileFailed
      ? 'VWorld 지도 로딩 실패'
      : '';

  return (
    <div className="map-frame">
      <DeckGL
        controller
        getTooltip={makeTooltip}
        layers={layers}
        viewState={viewState}
        onViewStateChange={({ viewState: nextViewState }) => setViewState(nextViewState)}
      />
      <div className="map-overlay-card">
        <strong>{overlayTitle}</strong>
        <span>{overlayDescription}</span>
      </div>
      {failureMessage ? <div className="map-error">{failureMessage}</div> : null}
      {dataFailed ? <div className="map-data-error">吏???덉씠???곗씠??濡쒕뵫 ?ㅽ뙣</div> : null}
      {landuseFailed ? <div className="map-data-error">?좎??댁슜 ?곗씠??濡쒕뵫 ?ㅽ뙣</div> : null}
      {developmentFailed ? <div className="map-data-error">媛쒕컻?ㅽ쁽???곗씠??濡쒕뵫 ?ㅽ뙣</div> : null}
      {jobsFailed ? <div className="map-data-error">吏곸＜쨌?곗뾽 ?곗씠??濡쒕뵫 ?ㅽ뙣</div> : null}
      {accessibilityFailed ? <div className="map-data-error">접근성 데이터 로딩 실패</div> : null}
      <MapLegend
        analysisLayer={analysisLayer}
        accessibilityTimeMode={accessibilityTimeMode}
        developmentLegendItems={developmentLegendItems}
        jobsMetric={jobsMetric}
        layerVisibility={visibility}
        metricRange={jobsMetricRange}
        showDetailedLegend={showDetailedLegend}
      />
      <div className="map-attribution">VWorld Base Map</div>
    </div>
  );
}

export function ControlledDashboardMap({
  viewMode,
  overlayTitle,
  overlayDescription,
  analysisLayer = 'base',
  layerVisibility,
  jobsMetric = 'worker_count_allocated',
  accessibilityTimeMode = 'all',
  showDetailedLegend = true,
}) {
  const apiKey = import.meta.env.VITE_VWORLD_KEY;
  const [viewState, setViewState] = useState(MAP_VIEWS[viewMode] ?? MAP_VIEWS.comparison);
  const [tileFailed, setTileFailed] = useState(false);
  const { boundaries, stations, failed: dataFailed } = useDashboardMapData();
  const { zones, missing, blockTypes, failed: landuseFailed } = useLanduseMapData(analysisLayer === 'landuse');
  const { buildings, failed: developmentFailed } = useDevelopmentMapData(analysisLayer === 'development');
  const { census, failed: jobsFailed } = useJobsMapData(analysisLayer === 'jobs');
  const { isochrones, stationBuffers, failed: accessibilityFailed } = useAccessibilityMapData(analysisLayer === 'accessibility');
  const visibility = {
    zoning: true,
    blockType: true,
    buildingParcel: true,
    vacant: true,
    census: true,
    station: true,
    ...layerVisibility,
  };
  const jobsMetricRange = useMemo(() => getJobsMetricRange(census, jobsMetric, viewMode), [census, jobsMetric, viewMode]);
  const developmentLegendItems = useMemo(
    () => getDevelopmentLegendItems(buildings, viewMode),
    [buildings, viewMode],
  );

  useEffect(() => {
    setViewState(MAP_VIEWS[viewMode] ?? MAP_VIEWS.comparison);
  }, [viewMode]);

  const layers = useMemo(() => {
    const baseLayer = createBaseMapLayer({ apiKey, tileFailed, setTileFailed, id: `vworld-base-map-${viewMode}` });
    return [
      baseLayer,
      ...(analysisLayer === 'landuse'
        ? createLanduseLayers({ boundaries, zones, missing, blockTypes, scope: viewMode, visibility })
        : analysisLayer === 'development'
          ? createDevelopmentLayers({ boundaries, buildings, scope: viewMode, visibility })
          : analysisLayer === 'jobs'
            ? createJobsLayers({ census, scope: viewMode, visibility, metric: jobsMetric, metricRange: jobsMetricRange })
            : analysisLayer === 'accessibility'
              ? createAccessibilityLayers({ boundaries, stations, isochrones, scope: viewMode, timeMode: accessibilityTimeMode })
                  .concat(createStationBufferLayers({ stationBuffers, scope: viewMode, visibility }))
                  .concat(createAccessibilityBoundaryAndStationLayers({ boundaries, stations, scope: viewMode, visibility }))
        : []),
      ...createOverlayLayers({
        boundaries: analysisLayer === 'jobs' || analysisLayer === 'base' ? boundaries : null,
        stations: visibility.station && analysisLayer !== 'accessibility' ? stations : null,
        scope: viewMode,
        subduedBoundary: analysisLayer !== 'base',
      }),
    ].filter(Boolean);
  }, [accessibilityTimeMode, analysisLayer, apiKey, blockTypes, boundaries, buildings, census, isochrones, jobsMetric, jobsMetricRange, layerVisibility, missing, stationBuffers, stations, tileFailed, viewMode, zones]);

  const failureMessage = !apiKey
    ? 'VWorld API 키가 설정되지 않았습니다.'
    : tileFailed
      ? 'VWorld 지도 로딩 실패'
      : '';

  return (
    <div className="map-frame">
      <DeckGL
        controller
        getTooltip={makeTooltip}
        layers={layers}
        viewState={viewState}
        onViewStateChange={({ viewState: nextViewState }) => setViewState(nextViewState)}
      />
      <div className="map-overlay-card">
        <strong>{overlayTitle}</strong>
        <span>{overlayDescription}</span>
      </div>
      {failureMessage ? <div className="map-error">{failureMessage}</div> : null}
      {dataFailed ? <div className="map-data-error">吏???덉씠???곗씠??濡쒕뵫 ?ㅽ뙣</div> : null}
      {landuseFailed ? <div className="map-data-error">?좎??댁슜 ?곗씠??濡쒕뵫 ?ㅽ뙣</div> : null}
      {developmentFailed ? <div className="map-data-error">媛쒕컻?ㅽ쁽???곗씠??濡쒕뵫 ?ㅽ뙣</div> : null}
      {jobsFailed ? <div className="map-data-error">吏곸＜쨌?곗뾽 ?곗씠??濡쒕뵫 ?ㅽ뙣</div> : null}
      {accessibilityFailed ? <div className="map-data-error">접근성 데이터 로딩 실패</div> : null}
      <MapLegend
        analysisLayer={analysisLayer}
        accessibilityTimeMode={accessibilityTimeMode}
        developmentLegendItems={developmentLegendItems}
        jobsMetric={jobsMetric}
        layerVisibility={visibility}
        metricRange={jobsMetricRange}
        showDetailedLegend={showDetailedLegend}
      />
      <div className="map-attribution">VWorld Base Map</div>
    </div>
  );
}

function MapLegend({
  analysisLayer = 'base',
  layerVisibility = {},
  jobsMetric = 'worker_count_allocated',
  accessibilityTimeMode = 'all',
  metricRange,
  showDetailedLegend = true,
  developmentLegendItems = DEVELOPMENT_MAIN_USE_LEGEND,
}) {
  return (
    <div className="map-legend" aria-label="지도 범례">
      {analysisLayer === 'landuse' ? (
        <>
          <div className="legend-row">
            <span className="legend-swatch missing" />
            <span>데이터 없음</span>
          </div>
          {layerVisibility.blockType ? (
            <div className="legend-row">
              <span className="legend-line blocktype" />
              <span>blockType</span>
            </div>
          ) : null}
        </>
      ) : null}
      {analysisLayer === 'development' ? (
        <>
          {layerVisibility.buildingParcel ? (
            <LegendGroup items={developmentLegendItems} title="주용도 — 주요 용도" />
          ) : null}
          {layerVisibility.vacant ? (
            <div className="legend-row">
              <span className="legend-swatch development-vacant" />
              <span>미건축·공지 추정</span>
            </div>
          ) : null}
        </>
      ) : null}
      {analysisLayer === 'jobs' ? (
        <>
          {layerVisibility.census ? (
            <div className="legend-group">
              <strong>{`${getJobsMetricConfig(jobsMetric).label} 기준`}</strong>
              {jobsMetric === 'jobs_balance' ? (
                <>
                  <div className="legend-row">
                    <span className="legend-swatch jobs-balance-employment" />
                    <span>고용 우세</span>
                  </div>
                  <div className="legend-row">
                    <span className="legend-swatch jobs-balance-residential" />
                    <span>주거 우세</span>
                  </div>
                  <div className="legend-row">
                    <span className="legend-swatch jobs-balance-mixed" />
                    <span>혼합형</span>
                  </div>
                  <div className="legend-row">
                    <span className="legend-swatch missing" />
                    <span>데이터 없음</span>
                  </div>
                </>
              ) : (
                <>
                  <div className="legend-row">
                    <span>낮음 → 높음</span>
                  </div>
                  <div className="legend-row">
                    <span className="legend-swatch jobs-low" />
                    <span>{metricRange ? `낮음 ${formatJobsMetricValue(metricRange.min, getJobsMetricConfig(jobsMetric).unit)}` : '낮음'}</span>
                  </div>
                  <div className="legend-row">
                    <span className="legend-swatch jobs-high" />
                    <span>{metricRange ? `높음 ${formatJobsMetricValue(metricRange.max, getJobsMetricConfig(jobsMetric).unit)}` : '높음'}</span>
                  </div>
                  <div className="legend-row">
                    <span>{`단위: ${getJobsMetricConfig(jobsMetric).unit}`}</span>
                  </div>
                  <div className="legend-row">
                    <span className="legend-swatch missing" />
                    <span>데이터 없음</span>
                  </div>
                </>
              )}
            </div>
          ) : null}
        </>
      ) : null}
      {analysisLayer === 'accessibility' ? (
        <div className="legend-group">
          <strong>등시간권</strong>
          {layerVisibility.station1km ? (
            <div className="legend-row">
              <span className="legend-swatch station-buffer-1000" />
              <span>1km 역세권</span>
            </div>
          ) : null}
          {layerVisibility.station500m ? (
            <div className="legend-row">
              <span className="legend-swatch station-buffer-500" />
              <span>500m 역세권</span>
            </div>
          ) : null}
          {(accessibilityTimeMode === 'all' || accessibilityTimeMode === '60') ? (
            <div className="legend-row">
              <span className="legend-swatch accessibility-60" />
              <span>60분 이내</span>
            </div>
          ) : null}
          {(accessibilityTimeMode === 'all' || accessibilityTimeMode === '30') ? (
            <div className="legend-row">
              <span className="legend-swatch accessibility-30" />
              <span>30분 이내</span>
            </div>
          ) : null}
          <div className="legend-row">
            <span className="legend-dot" />
            <span>핵심역</span>
          </div>
        </div>
      ) : null}
      {layerVisibility.station && analysisLayer !== 'accessibility' ? (
        <div className="legend-row">
          <span className="legend-dot" />
          <span>핵심역</span>
        </div>
      ) : null}
    </div>
  );
}

function LegendGroup({ items, title }) {
  const safeItems = Array.isArray(items) ? items : [];

  return (
    <div className="legend-group">
      <strong>{title}</strong>
      {safeItems.map((item) => (
        <div className="legend-row" key={item.label}>
          <span className="legend-color" style={{ backgroundColor: `rgb(${item.color.join(',')})` }} />
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  );
}












