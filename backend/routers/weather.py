#实时天气接口
import os
import requests
from datetime import datetime
from fastapi import APIRouter, HTTPException, Response, Query
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/weather", tags=["weather"])


def build_weather_advice(weather: str, temperature: str, wind_power: str):
    base = f"当前天气为{weather}，气温约{temperature}℃，风力{wind_power}。"

    if "雨" in weather:
        return base + " 老君山属于山地型景区，雨天道路湿滑，建议减少高强度徒步，优先选择索道和较稳妥的初阶路线。"

    if "雪" in weather:
        return base + " 雪天山地道路风险较高，应关注景区公告和索道运行情况，不建议选择高阶徒步路线。"

    if "晴" in weather or "多云" in weather:
        return base + " 当前天气较适合观景，可优先考虑十里画屏、马鬃岭、金顶道观群等核心景观节点。"

    if "雾" in weather or "霾" in weather:
        return base + " 能见度可能受影响，观景体验可能下降，建议关注山顶区域天气变化。"

    return base + " 建议结合个人体力、景区公告和现场天气变化选择游览路线。"

@router.get("/luanchuan")
def get_luanchuan_weather(
    response: Response,
    city: str = Query("410324", description="高德行政区划 adcode，默认栾川县")
):
    """
    查询栾川县实时天气。
    city 使用栾川县 adcode：410324。
    """
    response.headers["Cache-Control"] = "no-store"

    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        raise HTTPException(status_code=500, detail="未配置 AMAP_KEY，请检查 backend/.env 文件")

    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    params = {
        "key": amap_key,
        "city": city,
        "extensions": "base",
        "output": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("status") != "1":
            raise HTTPException(
                status_code=500,
                detail=f"高德天气接口异常：{data.get('info', '未知错误')}"
            )

        lives = data.get("lives", [])

        if not lives:
            raise HTTPException(status_code=404, detail="高德接口未返回天气 lives 数据")

        item = lives[0]

        weather = item.get("weather", "")
        temperature = item.get("temperature", "")
        wind_direction = item.get("winddirection", "")
        wind_power = item.get("windpower", "")
        humidity = item.get("humidity", "")
        report_time = item.get("reporttime", "")

        fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "city": item.get("city", "栾川县"),
            "adcode": item.get("adcode", "410324"),
            "weather": weather,
            "temperature": temperature,
            "winddirection": wind_direction,
            "windpower": wind_power,
            "humidity": humidity,
            "reporttime": report_time,
            "fetched_at": fetched_at,
            "advice": build_weather_advice(weather, temperature, wind_power)
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求高德天气失败：{str(e)}")