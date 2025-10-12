// ResultsView.swift

import SwiftUI
import AVFoundation

struct ResultsView: View {
    let menuData: [MenuCategory]
    @StateObject private var ttsManager = TTSManager()

    var body: some View {
        ZStack {
            Color.appBackground.ignoresSafeArea()

            VStack(spacing: 0) {
                Text("ANALYSIS")
                    .font(.custom("BudokanRounded-Bold", size: 40))
                    .foregroundColor(.appAccent)
                    .padding()

                List {
                    ForEach(menuData) { category in
                        Section(header: Text(category.category)
                            .font(.custom("BudokanRounded-Bold", size: 24))
                            .foregroundColor(.appAccent)
                        ) {
                            ForEach(category.items) { item in
                                FoodItemCard(item: item, ttsManager: ttsManager)
                            }
                        }
                    }
                }
                .listStyle(InsetGroupedListStyle())
                .background(Color.appBackground)
                
                bottomNavBar
            }
            
        }
        .navigationBarHidden(true)
        
    }
    
    var bottomNavBar: some View {
        HStack {
            Spacer()
            NavigationLink(destination: CameraView()) {
                Image(systemName: "camera").font(.largeTitle)
            }
            Spacer()
            NavigationLink(destination: MenuView()) {
                Image(systemName: "house.fill").font(.largeTitle)
            }
            Spacer()
            NavigationLink(destination: LoginView()) {
                Image(systemName: "person").font(.largeTitle)
            }
            Spacer()
        }
        .foregroundColor(.appAccent)
        .padding(.top, 15)
        .padding(.bottom, 30)
        .background(Color.appTextField.ignoresSafeArea())
    }
}

// --- TTS Manager ---
class TTSManager: ObservableObject {
    private var audioPlayer: AVAudioPlayer?
    @Published var isLoading = false
    
    init() {
        // Configure audio session
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Failed to set up audio session: \(error)")
        }
    }
    
    func speak(nutrient: String) {
        guard !isLoading else { return }
        
        isLoading = true
        
        // Replace with your actual backend URL
        let baseURL = "http://152.23.91.63:8000"
        let urlString = "\(baseURL)/explain/\(nutrient.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? nutrient)"
        
        guard let url = URL(string: urlString) else {
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                guard let data = data, error == nil else {
                    print(" TTS Error: \(error?.localizedDescription ?? "Unknown error")")
                    return
                }
                
                print("Received audio data: \(data.count) bytes")
                
                // Check HTTP response
                if let httpResponse = response as? HTTPURLResponse {
                    print("Status code: \(httpResponse.statusCode)")
                }
                
                do {
                    self?.audioPlayer = try AVAudioPlayer(data: data)
                    self?.audioPlayer?.prepareToPlay()
                    let success = self?.audioPlayer?.play() ?? false
                    print(success ? "Audio playing" : "Audio failed to play")
                    print("Duration: \(self?.audioPlayer?.duration ?? 0)s")
                } catch {
                    print("Audio playback error: \(error)")
                }
            }
        }.resume()
    }
}

// --- A Reusable Card for a Single Food Item ---
struct FoodItemCard: View {
    let item: FoodItem
    @ObservedObject var ttsManager: TTSManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            // --- Name and Price ---
            HStack {
                Text(item.name)
                    .font(.custom("BudokanRounded-Bold", size: 22))
                Spacer()
                if let price = item.price {
                    Text(String(format: "$%.2f", price))
                }
            }
            .foregroundColor(.appAccent)
            
            // --- Description ---
            if let description = item.description {
                Text(description)
                    .font(.custom("BudokanRounded-Bold", size: 16))
                    .foregroundColor(.appAccent.opacity(0.8))
            }
            
            // --- Meal Value Score ---
            if let mealValueScore = item.meal_value_score, !mealValueScore.isEmpty {
                HStack(spacing: 8) {
                    Image(systemName: "star.fill")
                        .foregroundColor(.yellow)
                        .font(.caption)
                    Text("Meal Value Score:")
                        .font(.custom("BudokanRounded-Bold", size: 14))
                        .foregroundColor(.appAccent)
                    Text(String(format: "%.1f", mealValueScore[0]))
                        .font(.custom("BudokanRounded-Bold", size: 16))
                        .foregroundColor(.yellow)
                        .bold()
                }
                .padding(.vertical, 6)
                .padding(.horizontal, 12)
                .background(Color.yellow.opacity(0.15))
                .cornerRadius(8)
            }
            
            // --- Dietary Restrictions ---
            if let restrictions = item.dietary_restrictions, !restrictions.isEmpty {
                HStack {
                    ForEach(restrictions, id: \.self) { restriction in
                        Text(restriction)
                            .font(.caption.bold())
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.green.opacity(0.2))
                            .cornerRadius(10)
                    }
                }
            }
            
            // --- Nutrition Info (Tappable) ---
            if let nutrition = item.nutrition {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text("Nutrition (tap to hear)")
                            .font(.caption.bold())
                        if ttsManager.isLoading {
                            ProgressView()
                                .scaleEffect(0.7)
                        }
                    }
                    
                    HStack(spacing: 12) {
                        if let calories = nutrition.calories {
                            NutrientButton(label: "Calories", value: "\(Int(calories))", ttsManager: ttsManager)
                        }
                        if let protein = nutrition.protein_g {
                            NutrientButton(label: "Protein", value: "\(Int(protein))g", ttsManager: ttsManager)
                        }
                        if let carbs = nutrition.carbs_g {
                            NutrientButton(label: "Carbohydrates", value: "\(Int(carbs))g", ttsManager: ttsManager)
                        }
                        if let fat = nutrition.fat_g {
                            NutrientButton(label: "Fat", value: "\(Int(fat))g", ttsManager: ttsManager)
                        }
                    }
                    
                    HStack(spacing: 12) {
                        if let fiber = nutrition.fiber_g {
                            NutrientButton(label: "Fiber", value: "\(Int(fiber))g", ttsManager: ttsManager)
                        }
                        if let sugar = nutrition.sugar_g {
                            NutrientButton(label: "Sugars", value: "\(Int(sugar))g", ttsManager: ttsManager)
                        }
                    }
                }
                .foregroundColor(.gray)
            }
        }
        .padding()
    }
}

// --- Tappable Nutrient Button ---
struct NutrientButton: View {
    let label: String
    let value: String
    @ObservedObject var ttsManager: TTSManager
    @State private var isPressed = false
    
    var body: some View {
        Button(action: {
            isPressed = true
            ttsManager.speak(nutrient: label)
            
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                isPressed = false
            }
        }) {
            VStack(spacing: 2) {
                Text(label)
                    .font(.caption2)
                    .fontWeight(.medium)
                Text(value)
                    .font(.caption)
                    .fontWeight(.bold)
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 6)
            .background(isPressed ? Color.blue.opacity(0.3) : Color.gray.opacity(0.15))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.blue.opacity(0.3), lineWidth: 1)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}
