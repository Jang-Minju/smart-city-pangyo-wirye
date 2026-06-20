import React, { useEffect, useMemo, useState } from 'react';
import DeckGL from '@deck.gl/react';
import { BitmapLayer, GeoJsonLayer, PathLayer, ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import { TileLayer } from '@deck.gl/geo-layers';
import proj4 from 'proj4';

const dataUrl = (path) => `${import.meta.env.BASE_URL}${String(path).replace(/^\/+/, '')}`;

const PANGYO_VIEW = {
  longitude: 127.111,
  latitude: 37.394,
  zoom: 14.2,
  pitch: 0,
  bearing: 0,
};

const EPSG_5186 = '+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=600000 +ellps=GRS80 +units=m +no_defs';
const EPSG_4326 = 'EPSG:4326';
const TILE_SIZE = 256;

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

function transformFeatureCollection(collection) {
  return {
    ...collection,
    features: (collection.features ?? []).map((feature) => ({
      ...feature,
      geometry: {
        ...feature.geometry,
        coordinates: transformCoordinates(feature.geometry.coordinates),
      },
    })),
  };
}

function makeBaseMapLayer({ apiKey, tileFailed, setTileFailed }) {
  if (!apiKey || tileFailed) {
    return null;
  }

  return new TileLayer({
    id: 'boundary-editor-vworld-base',
    data: `https://api.vworld.kr/req/wmts/1.0.0/${apiKey}/Base/{z}/{y}/{x}.png`,
    minZoom: 0,
    maxZoom: 19,
    tileSize: TILE_SIZE,
    onTileError: () => setTileFailed(true),
    renderSubLayers: (props) => {
      const { bbox } = props.tile;
      return new BitmapLayer(props, {
        id: `${props.id}-bitmap`,
        data: [0],
        image: props.data,
        bounds: [bbox.west, bbox.south, bbox.east, bbox.north],
      });
    },
  });
}

function closeRing(points) {
  if (points.length === 0) {
    return [];
  }

  return [...points, points[0]];
}

function createPolygonFeature(points) {
  return {
    type: 'Feature',
    properties: {
      name: 'pangyo_boundary_user_drawn',
      source: 'dashboard_boundary_editor_click_vertices',
      crs: 'EPSG:4326',
      vertex_count: points.length,
    },
    geometry: {
      type: 'Polygon',
      coordinates: [closeRing(points)],
    },
  };
}

function downloadGeoJson(points) {
  if (points.length < 3) {
    return;
  }

  const collection = {
    type: 'FeatureCollection',
    features: [createPolygonFeature(points)],
  };
  const blob = new Blob([JSON.stringify(collection, null, 2)], {
    type: 'application/geo+json;charset=utf-8',
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'pangyo_boundary_user_drawn.geojson';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function BoundaryEditor() {
  const apiKey = import.meta.env.VITE_VWORLD_KEY;
  const [viewState, setViewState] = useState(PANGYO_VIEW);
  const [tileFailed, setTileFailed] = useState(false);
  const [referenceBoundary, setReferenceBoundary] = useState(null);
  const [parcelReference, setParcelReference] = useState(null);
  const [points, setPoints] = useState([]);
  const [closed, setClosed] = useState(false);
  const [dataFailed, setDataFailed] = useState(false);

  useEffect(() => {
    let ignore = false;

    async function loadReferenceLayers() {
      try {
        const [boundaryResponse, parcelResponse] = await Promise.all([
          fetch(dataUrl('data/pangyo_boundary.geojson')),
          fetch(dataUrl('data/buildings_or_parcels.geojson')),
        ]);

        if (!boundaryResponse.ok) {
          throw new Error('boundary fetch failed');
        }

        const boundary = transformFeatureCollection(await boundaryResponse.json());
        let parcels = null;

        if (parcelResponse.ok) {
          const parcelData = await parcelResponse.json();
          parcels = transformFeatureCollection({
            ...parcelData,
            features: (parcelData.features ?? []).filter(
              (feature) => feature.properties?.area_name === 'pangyo_1st_technovalley',
            ),
          });
        }

        if (!ignore) {
          setReferenceBoundary(boundary);
          setParcelReference(parcels);
          setDataFailed(false);
        }
      } catch {
        if (!ignore) {
          setDataFailed(true);
        }
      }
    }

    loadReferenceLayers();

    return () => {
      ignore = true;
    };
  }, []);

  const drawingFeature = useMemo(() => {
    if (points.length < 3) {
      return null;
    }

    return {
      type: 'FeatureCollection',
      features: [createPolygonFeature(points)],
    };
  }, [points]);

  const layers = useMemo(() => {
    const baseLayer = makeBaseMapLayer({ apiKey, tileFailed, setTileFailed });
    const pathData = points.length >= 2 ? [{ path: closed ? closeRing(points) : points }] : [];

    return [
      baseLayer,
      parcelReference &&
        new GeoJsonLayer({
          id: 'boundary-editor-parcel-reference',
          data: parcelReference,
          stroked: true,
          filled: false,
          getLineColor: [65, 105, 150, 95],
          getLineWidth: 1,
          lineWidthUnits: 'pixels',
        }),
      referenceBoundary &&
        new GeoJsonLayer({
          id: 'boundary-editor-existing-pangyo-boundary',
          data: referenceBoundary,
          stroked: true,
          filled: true,
          getFillColor: [40, 105, 180, 28],
          getLineColor: [20, 82, 170, 230],
          getLineWidth: 3,
          lineWidthUnits: 'pixels',
        }),
      drawingFeature &&
        new GeoJsonLayer({
          id: 'boundary-editor-drawn-polygon',
          data: drawingFeature,
          stroked: true,
          filled: true,
          getFillColor: [231, 45, 30, 42],
          getLineColor: [231, 30, 24, 235],
          getLineWidth: 3,
          lineWidthUnits: 'pixels',
        }),
      pathData.length > 0 &&
        new PathLayer({
          id: 'boundary-editor-drawn-path',
          data: pathData,
          getPath: (item) => item.path,
          getColor: [231, 30, 24, 245],
          getWidth: 3,
          widthUnits: 'pixels',
        }),
      points.length > 0 &&
        new ScatterplotLayer({
          id: 'boundary-editor-vertices',
          data: points.map((point, index) => ({ point, index })),
          getPosition: (item) => item.point,
          getRadius: 28,
          radiusMinPixels: 6,
          radiusMaxPixels: 10,
          getFillColor: [231, 30, 24, 245],
          getLineColor: [255, 255, 255, 245],
          getLineWidth: 2,
          lineWidthUnits: 'pixels',
          stroked: true,
        }),
      points.length > 0 &&
        new TextLayer({
          id: 'boundary-editor-vertex-labels',
          data: points.map((point, index) => ({ point, index })),
          getPosition: (item) => item.point,
          getText: (item) => String(item.index + 1),
          getSize: 11,
          getColor: [255, 255, 255, 255],
          getTextAnchor: 'middle',
          getAlignmentBaseline: 'center',
        }),
    ].filter(Boolean);
  }, [apiKey, closed, drawingFeature, parcelReference, points, referenceBoundary, tileFailed]);

  function handleMapClick(info) {
    if (closed || !info.coordinate) {
      return;
    }

    const [longitude, latitude] = info.coordinate;
    setPoints((current) => [...current, [longitude, latitude]]);
  }

  const canComplete = points.length >= 3;
  const canDownload = closed && canComplete;

  return (
    <main className="boundary-editor-shell">
      <section className="boundary-editor-header">
        <div>
          <p className="eyebrow">Development Tool</p>
          <h1>Pangyo Boundary Editor</h1>
          <span>Click vertices directly on the VWorld map. The exported boundary uses only clicked points.</span>
        </div>
        <a href="/" className="editor-link-button">
          Dashboard
        </a>
      </section>

      <section className="boundary-editor-layout">
        <aside className="boundary-editor-panel">
          <div className="panel-block">
            <h2>Drawing</h2>
            <div className="editor-stat">
              <span>Vertices</span>
              <strong>{points.length}</strong>
            </div>
            <div className="editor-actions">
              <button type="button" onClick={() => setPoints((current) => current.slice(0, -1))} disabled={points.length === 0 || closed}>
                Undo
              </button>
              <button
                type="button"
                onClick={() => {
                  setPoints([]);
                  setClosed(false);
                }}
                disabled={points.length === 0}
              >
                Reset
              </button>
              <button type="button" onClick={() => setClosed(true)} disabled={!canComplete || closed}>
                Complete
              </button>
              <button type="button" onClick={() => downloadGeoJson(points)} disabled={!canDownload}>
                Download GeoJSON
              </button>
            </div>
          </div>
          <div className="panel-block">
            <h2>Reference Layers</h2>
            <div className="editor-legend-row">
              <span className="editor-swatch existing" />
              <span>Existing pangyo_boundary</span>
            </div>
            <div className="editor-legend-row">
              <span className="editor-swatch parcels" />
              <span>PNU/building parcel reference</span>
            </div>
            <div className="editor-legend-row">
              <span className="editor-swatch drawn" />
              <span>User drawn boundary</span>
            </div>
          </div>
          <div className="panel-block note">
            <h2>Export Rule</h2>
            <p>Saved as EPSG:4326 lon/lat GeoJSON. Run the validation script after placing the downloaded file in the project root or providing its path.</p>
          </div>
        </aside>

        <div className="boundary-editor-map">
          <DeckGL
            controller
            layers={layers}
            viewState={viewState}
            onClick={handleMapClick}
            onViewStateChange={({ viewState: nextViewState }) => setViewState(nextViewState)}
          />
          {!apiKey ? <div className="map-error">VWorld API key is not configured.</div> : null}
          {tileFailed ? <div className="map-error">VWorld map loading failed.</div> : null}
          {dataFailed ? <div className="map-data-error">Reference layer loading failed.</div> : null}
          <div className="boundary-editor-help">
            {closed ? 'Polygon completed. Download GeoJSON or reset to draw again.' : 'Click the map to add vertices. Pan with drag, zoom with wheel.'}
          </div>
        </div>
      </section>
    </main>
  );
}
