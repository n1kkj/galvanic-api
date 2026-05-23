from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, TabularInline
from django.contrib import admin

from apps.core.models import Machine, Sensor


class SensorInline(TabularInline):
    model = Sensor
    extra = 0
    fields = (
        "name",
        "sensor_type",
        "unit",
        "min_threshold",
        "max_threshold",
        "is_active",
    )
    show_change_link = True


@admin.register(Machine)
class MachineAdmin(ModelAdmin):
    list_display = ("id", "name", "is_active", "sensors_count")
    search_fields = ("name",)
    list_filter = ("is_active",)
    inlines = [SensorInline]

    def sensors_count(self, obj):
        return obj.sensors.count()


@admin.register(Sensor)
class SensorAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "machine_link",
        "sensor_type",
        "unit",
        "min_threshold",
        "max_threshold",
        "is_active",
    )
    search_fields = ("name", "machine__name")
    list_filter = ("sensor_type", "is_active", "machine")
    readonly_fields = ("live_chart",)

    def machine_link(self, obj):
        url = reverse("admin:core_machine_change", args=[obj.machine_id])
        return format_html('<a href="{}">{}</a>', url, obj.machine.name)

    machine_link.short_description = "Станок"

    def live_chart(self, obj):
        if not obj.pk:
            return "Сохраните датчик, чтобы увидеть график"
        return mark_safe(
            f"""<div style="display:flex;gap:12px;align-items:center;margin-bottom:8px;">
  <label for="window-select"><b>Окно:</b></label>
  <select id="window-select">
    <option value="5">Последние 5 секунд</option>
    <option value="10">Последние 10 секунд</option>
    <option value="30">Последние 30 секунд</option>
    <option value="60" selected>Последние 60 секунд</option>
    <option value="120">Последние 120 секунд</option>
    <option value="300">Последние 5 минут</option>
    <option value="600">Последние 10 минут</option>
    <option value="1800">Последние 30 минут</option>
    <option value="all">За весь период</option>
  </select>
</div>
<div style="max-width:900px"><canvas id="chart"></canvas></div>
<div id="sensor-stats" style="margin-top:12px;padding:12px;border:1px solid #ddd;border-radius:8px;background:#fafafa"></div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const historyBaseUrl = `/api/v1/core/sensors/{obj.pk}/history/`;
const latestUrl = `/api/v1/core/sensors/{obj.pk}/latest/`;
const statsBaseUrl = `/api/v1/core/sensors/{obj.pk}/stats/`;
const minThreshold = {obj.min_threshold};
const maxThreshold = {obj.max_threshold};
const windowSelect = document.getElementById('window-select');
let windowValue = windowSelect.value;

const data = {{labels: [], datasets:[
  {{label:'{obj.get_sensor_type_display()} ({obj.unit})', data:[], borderColor:'#f97316', tension:0.35}},
  {{label:'Мин. порог', data:[], borderColor:'#ef4444', borderDash:[6,6], pointRadius:0, tension:0}},
  {{label:'Макс. порог', data:[], borderColor:'#3b82f6', borderDash:[6,6], pointRadius:0, tension:0}},
]}};
const chart = new Chart(document.getElementById('chart'), {{type:'line', data:data, options:{{animation:false, scales:{{x:{{display:true}}, y:{{display:true}}}}}}}});
let lastTimestamp = null;

function applyPoints(points) {{
  data.labels = [];
  data.datasets[0].data = [];
  data.datasets[1].data = [];
  data.datasets[2].data = [];
  points.forEach((p) => {{
    data.labels.push(new Date(p.timestamp).toLocaleTimeString());
    data.datasets[0].data.push(p.value);
    data.datasets[1].data.push(minThreshold);
    data.datasets[2].data.push(maxThreshold);
    lastTimestamp = p.timestamp;
  }});
  chart.update();
}}

async function loadHistory() {{
  const resp = await fetch(`${{historyBaseUrl}}?seconds=${{windowValue}}`, {{credentials: 'same-origin'}});
  if (!resp.ok) return;
  const points = await resp.json();
  applyPoints(points || []);
}}

function trimToWindow() {{
  if (windowValue === "all") return;
  const maxPoints = Math.max(Number(windowValue), 1);
  while (data.labels.length > maxPoints) {{
    data.labels.shift();
    data.datasets.forEach(ds => ds.data.shift());
  }}
}}

function renderStats(stats) {{
  const el = document.getElementById('sensor-stats');
  if (!stats || !stats.samples) {{
    el.innerHTML = '<b>Статистика:</b> пока недостаточно данных';
    return;
  }}
  el.innerHTML = `
    <b>Статистика (${{windowValue === "all" ? "за весь период" : `окно ${{windowValue}} сек`}})</b><br>
    Кол-во точек: <b>${{stats.samples}}</b><br>
    Текущее: <b>${{stats.last}}</b> {obj.unit}<br>
    Среднее: <b>${{stats.avg}}</b> {obj.unit}<br>
    Мин/Макс факт: <b>${{stats.min}}</b> / <b>${{stats.max}}</b> {obj.unit}<br>
    Выходов за пороги: <b>${{stats.out_of_range_count}}</b> (${{stats.out_of_range_percent}}%)
  `;
}}

async function tick() {{
  try {{
    const response = await fetch(latestUrl, {{credentials: 'same-origin'}});
    if (response.ok) {{
      const p = await response.json();
      if (p && p.timestamp && p.timestamp !== lastTimestamp) {{
        lastTimestamp = p.timestamp;
        data.labels.push(new Date(p.timestamp).toLocaleTimeString());
        data.datasets[0].data.push(p.value);
        data.datasets[1].data.push(minThreshold);
        data.datasets[2].data.push(maxThreshold);
        trimToWindow();
        chart.update();
      }}
    }}

    const statsResp = await fetch(`${{statsBaseUrl}}?seconds=${{windowValue}}`, {{credentials: 'same-origin'}});
    if (statsResp.ok) {{
      renderStats(await statsResp.json());
    }}
  }} catch (e) {{}}
}}

windowSelect.addEventListener('change', async (e) => {{
  windowValue = e.target.value;
  await loadHistory();
}});

loadHistory().then(() => tick());
setInterval(tick, 1000);
</script>"""
        )

    live_chart.short_description = (
        "График и статистика в реальном времени (REST polling)"
    )
