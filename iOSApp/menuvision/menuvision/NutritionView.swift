// A struct to represent a single dietary preference toggle
// Conforming to Codable allows it to be saved to UserDefaults.
struct DietaryPreference: Identifiable, Codable {
    let id = UUID()
    let name: String
    var isOn: Bool
}

import Foundation
import Combine // Needed for ObservableObject

// An ObservableObject to manage loading and saving preferences.
class PreferencesManager: ObservableObject {
    
    // @Published tells SwiftUI to refresh any view using this property when it changes.
    @Published var preferences: [DietaryPreference]
    
    // A unique key to save and retrieve the data from UserDefaults.
    private static let userDefaultsKey = "userDietaryPreferences"

    init() {
        // Try to load saved data when the manager is created.
        if let data = UserDefaults.standard.data(forKey: Self.userDefaultsKey),
           let decodedPreferences = try? JSONDecoder().decode([DietaryPreference].self, from: data) {
            self.preferences = decodedPreferences
            return
        }
        
        // If no saved data is found, load the default set.
        self.preferences = [
            DietaryPreference(name: "Vegan", isOn: false),
            DietaryPreference(name: "Vegetarian", isOn: false),
            DietaryPreference(name: "Gluten-Free", isOn: false),
            DietaryPreference(name: "Dairy-Free", isOn: false),
            DietaryPreference(name: "Nut Allergy", isOn: false),
        ]
    }
    
    func savePreferences() {
        // Encode the current preferences array into JSON and save to UserDefaults.
        if let encodedData = try? JSONEncoder().encode(preferences) {
            UserDefaults.standard.set(encodedData, forKey: Self.userDefaultsKey)
            print("Preferences saved successfully!")
        }
    }
}

import SwiftUI

struct NutritionView: View {
    // 1. Get access to the navigation environment.
    // This allows the view to dismiss itself.
    @Environment(\.presentationMode) var presentationMode

    // Using @StateObject to manage the lifecycle of the preferences manager.
    @StateObject private var preferencesManager = PreferencesManager()

    var body: some View {
        ZStack {
            Color.appBackground.ignoresSafeArea()

            VStack {
                Text("Preferences")
                    .themedTitle()
                    .padding(.bottom, 20)

                ScrollView {
                    VStack(spacing: 15) {
                        // The loop binds directly to the manager's published property.
                        ForEach($preferencesManager.preferences) { $preference in
                            Toggle(isOn: $preference.isOn) {
                                Text(preference.name)
                                    .font(.custom("BudokanRounded-Bold", size: 20))
                                    .foregroundColor(.appAccent)
                            }
                            .padding()
                            .background(Color.appTextField)
                            .cornerRadius(15)
                            .tint(.appAccent)
                        }
                    }
                    .padding(.horizontal, 30)
                }
                
                Spacer()

                Button(action: {
                    // 2. Save the preferences first.
                    preferencesManager.savePreferences()
                    
                    // 3. Then, tell the navigation stack to pop this view.
                    // This will automatically set shouldNavigateToNutrition back to false.
                    presentationMode.wrappedValue.dismiss()
                }) {
                    Text("Save")
                        .font(.custom("BudokanRounded-Bold", size: 22))
                        .fontWeight(.bold)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.appAccent)
                        .foregroundColor(.white)
                        .cornerRadius(15)
                        .shadow(radius: 3, y: 3)
                }
                .padding(.horizontal, 30)
                .padding(.bottom, 20)
            }
            .padding(.top, 40)
        }
        .navigationBarHidden(true)
    }
}

// Ensure you have your PreferencesManager and DietaryPreference struct defined
// as in the previous examples to handle saving/loading with UserDefaults.

// MARK: - Preview
struct NutritionView_Previews: PreviewProvider {
    static var previews: some View {
        NutritionView()
    }
}
