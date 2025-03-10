import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configure Google Gemini API with direct API key
client = genai.Client(api_key="AIzaSyBfyeioijtuTAO1Vig2r-b-82NmYIZQOHg")  # Using direct API key for testing

def estimate_fare(origin, destination, transport_type):
    prompt = f"""
    You are a ride pricing calculator in Ghana. Calculate the fare from {origin} to {destination} using {transport_type}.
    Consider these factors:
    - Average distance-based rates in Ghana
    - Current fuel prices
    - Type of vehicle: {transport_type}
    
    Respond ONLY with a JSON object in this exact format:
    {{
        "estimated_fare": <number>,
        "location_info": {{
            "address": "{destination}",
            "coordinates": null,
            "details": "<brief route description>"
        }}
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error estimating fare: {e}")
        return {
            "estimated_fare": 0,
            "location_info": {
                "address": destination,
                "coordinates": None,
                "details": f"Error: {str(e)}"
            }
        }

def get_location_details(location):
    prompt = f"""
    Provide information about {location} in Ghana.
    Return ONLY a JSON object in this format:
    {{
        "address": "{location}",
        "landmarks": "<key landmarks>",
        "traffic": "<traffic info>",
        "safety": "<safety info>"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error getting location details: {e}")
        return {
            "address": location,
            "landmarks": "Not available",
            "traffic": "Not available",
            "safety": "Not available"
        }


if __name__ == "__main__":
    # Test the fare estimation
    test_result = estimate_fare("Accra Mall", "Kotoka Airport", "taxi")
    print("Test Fare Estimation:")
    print(test_result)