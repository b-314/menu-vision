// Models.swift

import Foundation

struct MenuItem: Decodable, Identifiable {
    let id = UUID() // For SwiftUI lists
    let name: String
    let price: Double
    let satietyScore: Double
    
    // --- NEW FINANCIAL DATA ---
    let valueGrade: String         // The overall "A" through "F" grade
    let caloriesPerDollar: Double
    let satietyPerDollar: Double   // How much "fullness" you get per dollar
}