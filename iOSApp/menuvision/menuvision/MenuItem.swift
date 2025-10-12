//
//  MenuItem.swift
//  menuvision
//
//  Created by Emily Jon on 10/11/25.
//


// Models.swift

import Foundation

struct MenuItem: Decodable, Identifiable {
    // These properties will be decoded from JSON
    let name: String
    let price: Double
    let satietyScore: Double
    let mealValue: Int
    let dietaryRestrictions: [DietaryRestriction]
    let nutritionInfo: [String]
    //let meal_value_score: [Float]
    
    // This property is for SwiftUI only and will not be decoded
    let id = UUID()
    
    // This tells the decoder to ignore the 'id' property
    enum CodingKeys: String, CodingKey {
        case name, price, satietyScore, mealValue, dietaryRestrictions, nutritionInfo
    }
}

struct DietaryRestriction: Decodable, Identifiable {
    // These properties will be decoded from JSON
    let name: String
    let isMet: Bool
    
    // This property is for SwiftUI only
    let id = UUID()
    
    // This tells the decoder to ignore the 'id' property
    enum CodingKeys: String, CodingKey {
        case name, isMet
    }
}
