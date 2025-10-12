//
//  Models.swift
//  menuvision
//
//  Created by Emily Jon on 10/12/25.
//


import Foundation

// Matches the top-level object in the JSON array
struct MenuCategory: Decodable, Identifiable {
    let id = UUID()
    let category: String
    let items: [FoodItem]
    
    // Tells the decoder to ignore 'id'
    enum CodingKeys: String, CodingKey {
        case category, items
    }
}

// Matches an item within the "items" array
struct FoodItem: Decodable, Identifiable {
    let id = UUID()
    let name: String
    let description: String?
    let price: Double?
    let nutrition: NutritionInfo?
    let dietary_restrictions: [String]?
    let meal_value_score: [Float]?

    
    // Tells the decoder to ignore 'id'
    enum CodingKeys: String, CodingKey {
        case name, description, price, nutrition, dietary_restrictions, meal_value_score
    }
}

// Matches the "nutrition" object
struct NutritionInfo: Decodable {
    let calories: Double?
    let protein_g: Double?
    let carbs_g: Double?
    let fat_g: Double?
    let fiber_g: Double?
    let sugar_g: Double?


}
