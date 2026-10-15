import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright


mcp = FastMCP("weather-Israel")

FORECAST_URL = "https://www.weather2day.co.il/forecast"

# Global browser and page instances
browser_instance = None
page_instance = None


async def init_browser():
    """Initialize browser once"""
    global browser_instance, page_instance
    
    if browser_instance is None:
        playwright = await async_playwright().start()
        browser_instance = await playwright.chromium.launch(headless=False)
        page_instance = await browser_instance.new_page()
    
    return page_instance


@mcp.tool()
async def open_weather_forecast_israel() -> str:
    """Open the weather forecast website for Israel
    
    This tool opens the browser and navigates to the weather forecast page.
    """
    try:
        page = await init_browser()
        await page.goto(FORECAST_URL, wait_until="networkidle")
        await asyncio.sleep(2)
        return f"Successfully opened {FORECAST_URL}"
    except Exception as e:
        return f"Error opening weather page: {str(e)}"


@mcp.tool()
async def enter_weather_forecast_city_israel(city_name: str) -> str:
    """Enter a city name in the search field
    
    Args:
        city_name: Name of the city to search for (e.g., "תל אביב", "ירושלים", "חיפה")
    """
    try:
        page = await init_browser()

        search_input = page.locator("#city_search_forecast")
        await search_input.wait_for(timeout=10000)
        await search_input.click()
        await search_input.fill(city_name)
        await asyncio.sleep(1)
        return f"Successfully entered city name: {city_name}"
    except Exception as e:
        return f"Error entering city name: {str(e)}"


@mcp.tool()
async def select_weather_forecast_city_israel() -> str:
    """Select the first city from the autocomplete dropdown
    
    This tool clicks on the first suggestion in the dropdown list.
    """
    try:
        page = await init_browser()
        suggestion = page.locator("#city_search_forecastautocomplete-list div").first
        await suggestion.wait_for(timeout=10000)
        await suggestion.click()
        await asyncio.sleep(3)
        return "Successfully selected city from dropdown"
    except Exception as e:
        return f"Error selecting city: {str(e)}"


@mcp.tool()
async def get_weather_forecast_israel_content() -> str:
    """Extract and return the weather forecast content from the page (RAG)
    
    This tool extracts the weather information from the loaded page
    and provides it to the LLM for answering questions directly.
    """
    try:
        page = await init_browser()

        await page.wait_for_selector(".current-weather", timeout=15000)
        await page.wait_for_selector(".weather-details", timeout=15000)

        title = await page.text_content('h1') or ''
        current_weather = await page.text_content('.current-weather') or ''
        details = await page.text_content('.weather-details') or ''

        if not current_weather.strip() and not details.strip():
            return "No forecast content found on page. Make sure a city has been selected."

        cleaned = " ".join((title + ' ' + current_weather + ' ' + details).split())
        return cleaned[:3000]
    except Exception as e:
        return f"Error extracting forecast content: {str(e)}"



def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
