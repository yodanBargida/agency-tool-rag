import asyncio
import uuid
from src.database.vector_store import VectorStore
from src.tools.manager import ToolManager
from src.models.tool import ToolDefinition
from src.agents.orchestrator import ReActOrchestrator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage

async def run_verification():
    print("--- Starting Complex ReAct Verification ---")
    vs = VectorStore()
    tm = ToolManager(vs)
    orchestrator = ReActOrchestrator()

    # Define a massive toolset to test RAG filtering
    mock_tools = [

        # --- Financial Cluster ---

        ToolDefinition(
            id="stock_price_live",
            name="Live Stock Price",
            description="Get the real-time trading price for a stock ticker. Use only for current market value.",
            input_schema={"ticker": "string"},
            output_schema={"price": "float", "currency": "string"}
        ),
        ToolDefinition(
            id="stock_historical_daily",
            name="Historical Stock Data",
            description="Get historical closing prices for a stock ticker. Use for trends or past performance, not live price.",
            input_schema={"ticker": "string", "date": "string"},
            output_schema={"close_price": "float"}
        ),
        ToolDefinition(
            id="company_revenue_lookup",
            name="Corporate Revenue Lookup",
            description="Returns the annual or quarterly revenue for a corporation. Use for financial health checks.",
            input_schema={"company_name": "string", "year": "int"},
            output_schema={"revenue": "int"}
        ),
        ToolDefinition(
            id="dividend_history_tool",
            name="Dividend History",
            description="Provides a list of past dividend payments for a company. Use when users ask about 'payouts' or 'yield'.",
            input_schema={"ticker": "string"},
            output_schema={"dividends": "list"}
        ),
        ToolDefinition(
            id="slack_broadcast_v2",
            name="Slack Channel Notifier",
            description="Sends a formal announcement to a team Slack channel. Use for 'alerts' or 'channel' updates.",
            input_schema={"channel": "string", "text": "string"},
            output_schema={"status": "success"}
        ),
        ToolDefinition(
            id="slack_dm_direct",
            name="Slack DM Tool",
            description="Sends a private direct message to a specific user. Do not use for channel alerts.",
            input_schema={"user": "string", "text": "string"},
            output_schema={"status": "sent"}
        ),
        ToolDefinition(
            id="ms_teams_alert",
            name="Teams Workplace Alert",
            description="Sends a notification to a Microsoft Teams channel. Only use if 'Teams' or 'Workplace' is mentioned.",
            input_schema={"channel_id": "string", "msg": "string"},
            output_schema={"status": "delivered"}
        ),

        # --- Weather & Environment Cluster ---
        ToolDefinition(
            id="weather_current_global",
            name="Global Current Weather",
            description="Current temperature and conditions for any city worldwide. Best for general weather queries.",
            input_schema={"location": "string"},
            output_schema={"temp": "float", "condition": "string"}
        ),
        ToolDefinition(
            id="weather_forecast_hourly",
            name="Hourly Weather Forecast",
            description="Detailed hour-by-hour forecast for the next 24 hours. Use for specific times like 'at 2 PM'.",
            input_schema={"location": "string", "hour": "int"},
            output_schema={"temp": "float", "chance_of_rain": "int"}
        ),
        ToolDefinition(
            id="air_quality_index_api",
            name="AQI Checker",
            description="Returns AQI, PM2.5, and ozone levels. Use when users ask about 'smog' or 'health safety' outside.",
            input_schema={"location": "string"},
            output_schema={"aqi": "int", "status": "string"}
        ),
        ToolDefinition(
            id="weather_extreme_alerts",
            name="Severe Weather Alerts",
            description="Checks for active warnings (tornado, flood). Use only if user sounds concerned about safety.",
            input_schema={"location": "string"},
            output_schema={"alerts": "list"}
        ),
        ToolDefinition(
            id="weather_london_current",
            name="London Quick Weather",
            description="Returns ONLY the current temperature in London. Do not use for forecasts or air quality.",
            input_schema={"city": "string"},
            output_schema={"temp": "float"}
        ),
        ToolDefinition(
            id="health_safety_index",
            name="Outdoor Health Advisor",
            description="Analyzes if outdoor conditions are safe for walking/exercise based on AQI and smog. Use for 'healthy' or 'safe' walk queries.",
            input_schema={"location": "string"},
            output_schema={"safety_rating": "string", "reason": "string"}
        ),
        ToolDefinition(
            id="met_office_hourly_forecast",
            name="Official Hourly Forecast",
            description="Provides hour-by-hour weather data for tomorrow. Required for queries about specific future times like '2 PM'.",
            input_schema={"location": "string", "hour": "int", "day": "string"},
            output_schema={"temp": "float", "rain_prob": "int"}
        ),

        # --- Communication Cluster ---
        ToolDefinition(
            id="email_sender_internal",
            name="Internal Email Sender",
            description="Sends a text email to a colleague. Use for professional internal communication.",
            input_schema={"recipient": "string", "body": "string"},
            output_schema={"status": "sent"}
        ),
        ToolDefinition(
            id="slack_message_notifier",
            name="Slack Notifier",
            description="Posts a short alert to a Slack channel. Use for quick team notifications or heads-ups.",
            input_schema={"channel": "string", "message": "string"},
            output_schema={"status": "posted"}
        ),
        ToolDefinition(
            id="calendar_event_creator",
            name="Calendar Scheduler",
            description="Schedules a meeting on a user's calendar. Use for 'invites' or 'booking time'.",
            input_schema={"event_name": "string", "start_time": "string"},
            output_schema={"event_id": "string"}
        ),
        ToolDefinition(
            id="travel_time_estimator",
            name="Walking Distance Calculator",
            description="Calculates time to walk between points. Use for 'how long to get there' queries.",
            input_schema={"start": "string", "end": "string"},
            output_schema={"minutes": "int"}
        ),
        ToolDefinition(
            id="cafe_finder_london",
            name="London Cafe Locator",
            description="Finds cafes near a location. Use only if user asks 'where' to go.",
            input_schema={"area": "string"},
            output_schema={"cafes": "list"}
        ),
        ToolDefinition(
            id="timezone_checker",
            name="Global Time Sync",
            description="Checks the local time in different cities. Use for 'what time is it there' queries.",
            input_schema={"city": "string"},
            output_schema={"local_time": "string"}
        ),
        ToolDefinition(
            id="workday_status_api",
            name="Employee Presence Checker",
            description="Checks if team members are 'online' or 'staying in'. Use for 'is the team available' queries.",
            input_schema={"team_name": "string"},
            output_schema={"online_count": "int"}
        ),

        # --- Data & Calculations Cluster ---
        ToolDefinition(
            id="math_expression_evaluator",
            name="Formula Calculator",
            description="Calculates complex mathematical formulas. Use for equations and arithmetic.",
            input_schema={"expression": "string"},
            output_schema={"result": "float"}
        ),
        ToolDefinition(
            id="unit_converter_pro",
            name="Professional Unit Converter",
            description="Converts values between metric and imperial units. Use for distances, weights, and volumes.",
            input_schema={"value": "float", "from_unit": "string", "to_unit": "string"},
            output_schema={"converted_value": "float"}
        ),
        ToolDefinition(
            id="currency_converter_live",
            name="Live Currency Converter",
            description="Converts one currency to another using mid-market rates. Use for money conversion.",
            input_schema={"amount": "float", "from_currency": "string", "to_currency": "string"},
            output_schema={"result_amount": "float"}
        ),
        ToolDefinition(
            id="tax_calculator_simple",
            name="Sales Tax Calculator",
            description="Calculates sales tax or VAT for a given amount. Use for commerce and shopping queries.",
            input_schema={"amount": "float", "region": "string"},
            output_schema={"total_with_tax": "float"}
        )
   ]  
    for tool in mock_tools:
       tm.create_tool(tool)

    # TRAP QUERY: Requires Revenue -> Math (+5%) -> Currency (GBP) -> Slack (#investors-announcements)
    trap_query = (
        "I am looking at my historical portfolio and noticed a weird dip in my AAPL dividends last year. "
        "I need to calculate exactly how much more I would have earned in British Pounds if the revenue for Apple in 2023 had been 5% higher, "
        "so I can post a formal heads-up to the #investors-announcements Slack channel."
    )

    print(f"\nRunning High-Complexity Agent Loop...")
    result = await orchestrator.run(trap_query, str(uuid.uuid4()))

    print("\n" + "="*50)
    print("FINAL AGENT RESPONSE:")
    print(result.get("final_response"))
    print("="*50)

    print(f"\nTotal steps taken: {result.get('steps_count')}")
    print(f"Tools retrieved in last step: {[t.name for t in result.get('retrieved_tools')]}")
    
if __name__ == "__main__":
    asyncio.run(run_verification())