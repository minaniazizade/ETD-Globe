from pathlib import Path
import base64, json
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
DATA_DIR = ROOT / 'data'

st.set_page_config(page_title='ETD Globe', page_icon='🌍', layout='wide')
st.markdown('''<style>
@import url('');
.stApp{background:radial-gradient(circle at 50% 0%,#173451 0%,#081827 48%,#040a12 100%);color:#edf6ff}
.block-container{max-width:1450px;padding-top:1.4rem}
h1,h2,h3{color:#f4f8ff}
[data-testid="stMetric"]{background:#10283d;border:1px solid #294b65;padding:14px;border-radius:14px}
[data-testid="stMetricLabel"]{color:#a9c3d8}[data-testid="stMetricValue"]{color:#fff}
section[data-testid="stSidebar"]{background:#071522}
.small{color:#a9bfd1;font-size:.9rem}
</style>''', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def read_local_data(path):
    d = pd.read_csv(path)
    d.columns = [str(c).strip() for c in d.columns]
    if 'T2M_C' not in d and 'T2M' in d:
        d['T2M_C'] = pd.to_numeric(d['T2M'], errors='coerce') - 273.15
    needed = ['time','lat','lon','T2M_C']
    missing = [c for c in needed if c not in d]
    if missing: raise ValueError('Required columns are missing: ' + ', '.join(missing))
    d['time'] = pd.to_datetime(d['time'], errors='coerce')
    for c in ['lat','lon','T2M_C']: d[c] = pd.to_numeric(d[c], errors='coerce')
    d = d.dropna(subset=needed).copy()
    d['lon'] = ((d['lon'] + 180) % 360) - 180
    d['month'] = d['time'].dt.month
    d['time_period'] = d['time'].dt.to_period('M').astype(str)
    return d

@st.cache_data(show_spinner=False)
def load_geojson(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

@st.cache_data(show_spinner=False)
def country_summaries(frame, geojson_text):
    import geopandas as gpd
    from shapely.geometry import Point
    from shapely import wkt
    countries = gpd.read_file(geojson_text)

    ncol = 'name' if 'name' in countries.columns else 'ADMIN'
    icol = 'iso_a3' if 'iso_a3' in countries.columns else 'ADM0_A3'
    countries = countries[[ncol, icol, 'geometry']].rename(columns={ncol:'country', icol:'iso3'})

    pts = frame.groupby(['lat','lon','time_period'], as_index=False)['T2M_C'].mean()
    pg = gpd.GeoDataFrame(pts, geometry=gpd.points_from_xy(pts.lon, pts.lat), crs='EPSG:4326')
    joined = gpd.sjoin(pg, countries, how='inner', predicate='within')
    monthly = joined.groupby(['country','iso3','time_period'], as_index=False).agg(
        mean_c=('T2M_C','mean'), min_c=('T2M_C','min'), max_c=('T2M_C','max'), points=('T2M_C','size'))
    summary = monthly.groupby(['country','iso3'], as_index=False).agg(
        mean_c=('mean_c','mean'), min_c=('min_c','min'), max_c=('max_c','max'), months=('time_period','nunique'))
    stats = {str(r.iso3): {'country':str(r.country),'mean_c':float(r.mean_c),
            'min_c':float(r.min_c),'max_c':float(r.max_c),'months':int(r.months)}
            for r in summary.itertuples()}
    monthly_records = monthly.to_dict('records')
    return stats, monthly_records, summary

st.title('🌍 ETD Globe')
st.markdown('### Earth Temperature Detective')
st.markdown('<p class="small">Hello and welcome to ETD Globe Explore the world, and enjoy.</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header('Data Source')
    csv_upload = st.file_uploader('Choose CSV (optional)', type=['csv'])
    default_csv = ROOT / 'Dataset.csv'
    st.caption('Alternatively, place Dataset.csv next to app.py. Required columns: time, lat, lon, and T2M_C (or T2M in Kelvin).')
    st.divider()
    st.caption('Offline mode: the globe texture, country boundaries, and rendering code are loaded from local project files. No CDN or external map requests are used.')

try:
    if csv_upload is not None:
        df = pd.read_csv(csv_upload)
        df.columns = [str(c).strip() for c in df.columns]
        if 'T2M_C' not in df and 'T2M' in df: df['T2M_C'] = pd.to_numeric(df['T2M'], errors='coerce') - 273.15
        missing = [c for c in ['time','lat','lon','T2M_C'] if c not in df]
        if missing: raise ValueError('Missing columns: '+', '.join(missing))
        df['time']=pd.to_datetime(df.time,errors='coerce')
        for c in ['lat','lon','T2M_C']: df[c]=pd.to_numeric(df[c],errors='coerce')
        df=df.dropna(subset=['time','lat','lon','T2M_C']).copy()
        df['lon']=((df.lon+180)%360)-180
        df['month']=df.time.dt.month; df['time_period']=df.time.dt.to_period('M').astype(str)
    elif default_csv.exists():
        df = read_local_data(str(default_csv))
    else:
        st.warning('Place Dataset.csv next to app.py or upload it using the sidebar.')
        st.stop()
    if df.empty: st.error('No valid records were found in the CSV file.'); st.stop()
except Exception as e:
    st.error(f'Error while reading the dataset: {e}')
    st.stop()


geo_path = DATA_DIR / 'countries.geojson'
texture_path = ASSETS / 'earth_texture.jpg'
if not geo_path.exists() or not texture_path.exists():
    st.error('Local globe assets were not found. Keep the assets and data folders alongside app.py.')
    st.stop()
geo = load_geojson(str(geo_path))
geo_text = json.dumps(geo, separators=(',',':'))
texture_b64 = base64.b64encode(texture_path.read_bytes()).decode('ascii')

with st.spinner('Matching local temperature points to country boundaries...'):
    try:
        country_stats, monthly_country, country_table = country_summaries(df, str(geo_path))
    except Exception as e:
        st.error(f'Error while matching data points to country boundaries: {e}')
        st.info('Install the dependencies listed in requirements.txt.')
        st.stop()

# Build a self-contained canvas globe. All visual assets and country polygons are embedded locally.
payload = json.dumps({'geo':geo,'stats':country_stats,'monthly':monthly_country}, separators=(',',':'))
html = r'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#030b14;overflow:hidden;font-family:Arial,sans-serif}#stage{position:relative;width:100%;height:680px;background:radial-gradient(ellipse at 50% 48%,#10263a,#030b14 72%);overflow:hidden;border:1px solid #24445c;border-radius:18px}canvas{width:100%;height:100%;display:block;cursor:grab}canvas:active{cursor:grabbing}#panel{position:absolute;top:16px;left:16px;width:260px;max-width:calc(100% - 64px);padding:15px;background:rgba(3,16,29,.84);border:1px solid #355a72;border-radius:13px;color:#eef7ff;backdrop-filter:blur(8px);pointer-events:none}#eyebrow{font-size:10px;letter-spacing:2px;color:#72c9e8;font-weight:bold}#name{font-size:21px;font-weight:bold;margin:9px 0}#detail{font-size:12px;color:#abc3d5;line-height:1.5}#stats{display:none;margin-top:12px;font-size:12px;line-height:1.9}#hint{position:absolute;right:16px;bottom:14px;color:#a6c1d5;background:#061522c9;padding:8px 11px;border-radius:8px;font-size:11px}
</style></head><body><div id="stage"><canvas id="globe"></canvas><div id="panel"><div id="eyebrow">ETD GLOBE · EARTH TEMPERATURE DETECTIVE</div><div id="name">Earth in motion</div><div id="detail">Drag to rotate · Scroll to zoom · Click a country to inspect its data</div><div id="stats"></div></div><div id="hint">AUTO-ROTATION · DRAG TO ROTATE</div></div>
<script>
const DATA=__PAYLOAD__, TEX='data:image/jpeg;base64,__TEXTURE__';
const canvas=document.getElementById('globe'),ctx=canvas.getContext('2d',{alpha:true});
const img=new Image();img.src=TEX;let W=0,H=0,cx=0,cy=0,R=230,yaw=0.35,pitch=0.12,zoom=1,drag=false,lastX=0,lastY=0,auto=true,lastT=0;
const texCanvas=document.createElement('canvas'),tctx=texCanvas.getContext('2d',{willReadFrequently:true});let texData=null;
img.onload=()=>{texCanvas.width=img.width;texCanvas.height=img.height;tctx.drawImage(img,0,0);texData=tctx.getImageData(0,0,img.width,img.height).data;resize();requestAnimationFrame(loop)};
function resize(){const dpr=Math.min(window.devicePixelRatio||1,1.5);const r=canvas.getBoundingClientRect();W=Math.round(r.width*dpr);H=Math.round(r.height*dpr);canvas.width=W;canvas.height=H;cx=W*.57;cy=H*.52;R=Math.min(H*.39,W*.34)*zoom;}
window.addEventListener('resize',resize);
function rotate(v,a){let c=Math.cos(a),s=Math.sin(a);return [v[0]*c+v[2]*s,v[1],-v[0]*s+v[2]*c]}
function invRotate(v){let cp=Math.cos(pitch),sp=Math.sin(pitch),cyw=Math.cos(yaw),syw=Math.sin(yaw);let x=v[0],y=v[1],z=v[2];let y1=y*cp+z*sp,z1=-y*sp+z*cp;return [x*cyw-z1*syw,y1,x*syw+z1*cyw]}
function project(lon,lat){let lo=lon*Math.PI/180,la=lat*Math.PI/180;let v=[Math.cos(la)*Math.sin(lo),Math.sin(la),Math.cos(la)*Math.cos(lo)];v=rotate(v,yaw);let cp=Math.cos(pitch),sp=Math.sin(pitch);let yy=v[1]*cp-v[2]*sp,zz=v[1]*sp+v[2]*cp;return {x:cx+R*v[0],y:cy-R*yy,z:zz}}
function drawTexture(){if(!texData)return;let r=R,diam=Math.ceil(2*r),id=ctx.createImageData(diam,diam),out=id.data,tw=img.width,th=img.height;for(let py=0;py<diam;py++){let ny=(py-r)/r;for(let px=0;px<diam;px++){let nx=(px-r)/r,rr=nx*nx+ny*ny;if(rr>1)continue;let nz=Math.sqrt(1-rr);let v=invRotate([nx,-ny,nz]);let lon=Math.atan2(v[0],v[2]);let lat=Math.asin(Math.max(-1,Math.min(1,v[1])));let u=((lon/(2*Math.PI)+.5)*tw+tw)%tw;let vv=(.5-lat/Math.PI)*th;let ix=Math.min(tw-1,Math.max(0,Math.floor(u))),iy=Math.min(th-1,Math.max(0,Math.floor(vv)));let si=(iy*tw+ix)*4,di=(py*diam+px)*4;let light=Math.max(.22,Math.min(1.18,.62+.48*nz));let limb=Math.pow(nz,.22);out[di]=texData[si]*light;out[di+1]=texData[si+1]*light;out[di+2]=texData[si+2]*light;out[di+3]=Math.round(255*limb);}}let off=document.createElement('canvas');off.width=diam;off.height=diam;off.getContext('2d').putImageData(id,0,0);ctx.save();ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.clip();ctx.drawImage(off,cx-r,cy-r);ctx.restore();}
function drawStars(){ctx.fillStyle='#d8edff';for(let i=0;i<95;i++){let x=((i*7919)%997)/997*W,y=((i*3571)%991)/991*H;let a=.18+((i*13)%70)/100;ctx.globalAlpha=a;ctx.fillRect(x,y,1.2,1.2)}ctx.globalAlpha=1}
function drawGrid(){ctx.save();ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.clip();ctx.strokeStyle='rgba(173,220,240,.22)';ctx.lineWidth=.7;for(let lat=-60;lat<=60;lat+=30){let first=true;ctx.beginPath();for(let lon=-180;lon<=180;lon+=3){let p=project(lon,lat);if(p.z>0){if(first){ctx.moveTo(p.x,p.y);first=false}else ctx.lineTo(p.x,p.y)}else first=true}ctx.stroke()}for(let lon=-150;lon<=180;lon+=30){ctx.beginPath();let first=true;for(let lat=-88;lat<=88;lat+=2){let p=project(lon,lat);if(p.z>0){if(first){ctx.moveTo(p.x,p.y);first=false}else ctx.lineTo(p.x,p.y)}else first=true}ctx.stroke()}ctx.restore()}
function drawCountries(){ctx.save();ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.clip();ctx.strokeStyle='rgba(218,239,250,.48)';ctx.lineWidth=.55;for(const f of DATA.geo.features){let g=f.geometry;if(!g)continue;let polys=g.type==='Polygon'?[g.coordinates]:g.coordinates;for(const poly of polys){for(const ring of poly){ctx.beginPath();let started=false;for(const c of ring){let p=project(c[0],c[1]);if(p.z>0){if(!started){ctx.moveTo(p.x,p.y);started=true}else ctx.lineTo(p.x,p.y)}else started=false}ctx.stroke()}}}ctx.restore()}
function pointInRing(pt,ring){let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){let xi=ring[i][0],yi=ring[i][1],xj=ring[j][0],yj=ring[j][1];let hit=((yi>pt[1])!==(yj>pt[1]))&&(pt[0]<(xj-xi)*(pt[1]-yi)/(yj-yi+1e-12)+xi);if(hit)inside=!inside;}return inside}
function findCountry(lon,lat){for(const f of DATA.geo.features){let g=f.geometry;if(!g)continue;let polys=g.type==='Polygon'?[g.coordinates]:g.coordinates;for(const poly of polys){if(poly.length&&pointInRing([lon,lat],poly[0])){let inHole=poly.slice(1).some(r=>pointInRing([lon,lat],r));if(!inHole)return f}}}return null}
function showCountry(f){let nm=f?(f.properties.name||f.properties.ADMIN||'Selected country'):'No country selected';document.getElementById('name').textContent=nm;let iso=f?(f.properties.iso_a3||f.properties.ADM0_A3):'';let s=DATA.stats[iso];let box=document.getElementById('stats');if(!s){box.style.display='none';document.getElementById('detail').textContent='No matched temperature grid points were found for this country in your dataset.';return}document.getElementById('detail').textContent='Summary from available grid points in your uploaded dataset.';box.style.display='block';box.innerHTML=`<b>Mean T2M:</b> ${s.mean_c.toFixed(2)} °C<br><b>Minimum:</b> ${s.min_c.toFixed(2)} °C<br><b>Maximum:</b> ${s.max_c.toFixed(2)} °C<br><b>Available months:</b> ${s.months}`}
canvas.addEventListener('pointerdown',e=>{drag=true;auto=false;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(!drag)return;let dx=e.clientX-lastX,dy=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;yaw+=dx*.006;pitch=Math.max(-1.25,Math.min(1.25,pitch+dy*.006))});canvas.addEventListener('pointerup',e=>{drag=false});canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.72,Math.min(1.5,zoom*(e.deltaY>0?.93:1.07)));resize()},{passive:false});canvas.addEventListener('click',e=>{if(drag)return;let rect=canvas.getBoundingClientRect(),dpr=canvas.width/rect.width,x=(e.clientX-rect.left)*dpr,y=(e.clientY-rect.top)*dpr,nx=(x-cx)/R,ny=-(y-cy)/R,rr=nx*nx+ny*ny;if(rr>1)return;let v=invRotate([nx,ny,Math.sqrt(1-rr)]);let lon=Math.atan2(v[0],v[2])*180/Math.PI,lat=Math.asin(v[1])*180/Math.PI;showCountry(findCountry(lon,lat))});
function loop(t){if(!drag&&auto)yaw+=.00022*(t-lastT||16);lastT=t;ctx.clearRect(0,0,W,H);drawStars();let glow=ctx.createRadialGradient(cx,cy,R*.72,cx,cy,R*1.22);glow.addColorStop(0,'rgba(42,144,205,0)');glow.addColorStop(.72,'rgba(42,144,205,.12)');glow.addColorStop(1,'rgba(72,178,235,0)');ctx.fillStyle=glow;ctx.beginPath();ctx.arc(cx,cy,R*1.25,0,Math.PI*2);ctx.fill();drawTexture();drawGrid();drawCountries();ctx.strokeStyle='rgba(119,203,242,.62)';ctx.lineWidth=1.3;ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.stroke();requestAnimationFrame(loop)}
</script></body></html>'''
html = html.replace('__PAYLOAD__', payload).replace('__TEXTURE__', texture_b64)
components.html(html, height=700, scrolling=False)


st.divider(); st.header('Temperature Analysis')
a,b,c,d=st.columns(4)
a.metric('Records',f'{len(df):,}'); b.metric('Date range',f'{df.time.min():%Y-%m} — {df.time.max():%Y-%m}')
c.metric('Grid locations',f'{df[["lat","lon"]].drop_duplicates().shape[0]:,}'); d.metric('Mean T2M',f'{df.T2M_C.mean():.2f} °C')
region_boxes={'Greenland':(58,84,-75,-10),'Sahara Desert':(15,33,-17,35),'Amazon':(-20,5,-80,-45)}
region=st.selectbox('Select a study region',['Global sample','Greenland','Sahara Desert','Amazon'])
sub=df if region=='Global sample' else df[df.lat.between(region_boxes[region][0],region_boxes[region][1]) & df.lon.between(region_boxes[region][2],region_boxes[region][3])]
if not sub.empty:
    monthly=sub.groupby('time_period',as_index=False).agg(T2M_C=('T2M_C','mean'),records=('T2M_C','size'))
    monthly['time']=pd.to_datetime(monthly.time_period+'-01')
    fig=px.line(monthly,x='time',y='T2M_C',markers=True,title=f'Monthly Mean T2M — {region}')
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(7,20,34,.5)',yaxis_title='Temperature (°C)')
    st.plotly_chart(fig,use_container_width=True)
    season_n={12:'Winter',1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',6:'Summer',7:'Summer',8:'Summer',9:'Autumn',10:'Autumn',11:'Autumn'}
    season_s={12:'Summer',1:'Summer',2:'Summer',3:'Autumn',4:'Autumn',5:'Autumn',6:'Winter',7:'Winter',8:'Winter',9:'Spring',10:'Spring',11:'Spring'}
    season_map=season_s if region=='Amazon' else season_n
    seasonal=sub.copy(); seasonal['season']=seasonal.month.map(season_map)
    seasonal=seasonal.groupby('season',as_index=False).T2M_C.mean()
    fig2=px.bar(seasonal,x='season',y='T2M_C',color='T2M_C',color_continuous_scale='Temps',title='Seasonal Temperature Comparison')
    fig2.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(7,20,34,.5)',yaxis_title='Temperature (°C)')
    st.plotly_chart(fig2,use_container_width=True)
else: st.warning('No data points found in this region.')
with st.expander('Country Temperature Summary'):
    st.dataframe(country_table.sort_values('mean_c',ascending=False),use_container_width=True,hide_index=True)
st.caption('Offline build · Country boundaries: Natural Earth low-resolution data · Country means summarize matched grid points and are not automatically area-weighted national averages.')
