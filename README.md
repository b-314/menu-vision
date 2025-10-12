# Curate Plate 

An iOS app that uses AI to analyze restaurant menus and provide nutritional information from Gemini and NutritionIX, a meal value score, and text-to-speech explanations powered by ElevenLabs.

# Features

Camera integration: Capture menu images directly from your device

AI-Powered Menu Parsing: Extract menu items, prices, and descriptions automatically

Nutritional Analysis: Get estimated calories, protein, carbs, fat, fiber, and sugar for each menu item

Meal Value Score: AI-generated score to help you make informed dining choices

Text-to-Speech: Tap any nutrient to hear an explanation of its health benefits

Dietary Restrictions: Automatic detection of vegetarian, vegan, gluten-free options

Custom UI: Beautiful interface with custom BudokanRounded font and hand drawn graphics

## iOS App (Swift)
SwiftUI

AVFoundation for audio playback
Custom color scheme and typography

## Backend (Python)
FastAPI for API endpoints

ElevenLabs API for text-to-speech

AI/ML for menu parsing and nutritional analysis


# AI Components
## Menu Parsing

Uses Gemini  to analyze menu images
Extracts structured data: item names, descriptions, prices
Identifies dietary restrictions (vegetarian, vegan, gluten-free)
Handles various menu formats and layouts

## Nutritional Analysis

NutritionIX and Gemini estimates nutritional content based on item descriptions
Provides values for: calories, protein, carbohydrates, fat, fiber, sugars
Uses food composition databases and typical portion sizes
Returns structured JSON for consistent parsing

## Meal Value Scoring

AI calculates a 0-100 score based on nutritional density
Considers protein-to-calorie ratio, fiber content, and micronutrient density
Factors in price-to-nutrition value
Helps users identify the most nutritious options

## Text-to-Speech

ElevenLabs Multilingual v2 model
Natural-sounding voice explanations for 50+ nutrients
Optimized voice settings (stability: 0.4, similarity_boost: 0.8)
Streaming audio response for low latency

# Installation
### Backend Setup

1. Clone the repository

2. Install Python dependencies

3. Set up environment variables
  
5. Start the backend server

### iOS App Setup
1. Open the project in Xcode

2. 2. Configure the backend URL

3. Add required permissions

4. Install the custom font

# Usage

Launch the app and log in or create an account

Navigate to the camera view

Capture a menu image or upload from gallery

View analysis - AI processes the image and extracts menu information

Review nutritional estimates and meal value scores

# License
This project is licensed under the MIT License - see the LICENSE file for details.


# Acknowledgments

Google Gemini for Gemini and Gemini-2.5-flash APIs
ElevenLabs for text-to-speech API
Swift and FastAPI



