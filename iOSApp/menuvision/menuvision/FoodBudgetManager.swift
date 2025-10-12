import SwiftUI
import Combine

// ObservableObject to manage food budget
class FoodBudgetManager: ObservableObject {
    @Published var foodBudget: String = ""

    private static let userDefaultsKey = "foodBudget"

    init() {
        if let savedBudget = UserDefaults.standard.string(forKey: Self.userDefaultsKey) {
            self.foodBudget = savedBudget
        }
    }

    func saveBudget() {
        UserDefaults.standard.set(foodBudget, forKey: Self.userDefaultsKey)
        print("Food budget saved successfully!")
    }
}

struct FoodBudgetView: View {
    @Environment(\.presentationMode) var presentationMode
    @StateObject private var budgetManager = FoodBudgetManager()

    var body: some View {
        ZStack {
            Color.appBackground.ignoresSafeArea()

            VStack {
                Text("Food Budget")
                    .themedTitle()
                    .padding(.bottom, 20)

                VStack(spacing: 15) {
                    HStack {
                        Text("Budget Amount")
                            .font(.custom("BudokanRounded-Bold", size: 20))
                            .foregroundColor(.appAccent)
                        Spacer()
                        TextField("0", text: $budgetManager.foodBudget)
                            .keyboardType(.decimalPad)
                            .padding()
                            .frame(width: 120)
                            .background(Color.appTextField)
                            .cornerRadius(10)
                            .foregroundColor(.appAccent)
                    }
                    .padding()
                    .background(Color.appTextField.opacity(0.2))
                    .cornerRadius(15)
                    .padding(.horizontal, 30)
                }

                Spacer()

                Button(action: {
                    budgetManager.saveBudget()
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

// MARK: - Preview
struct FoodBudgetView_Previews: PreviewProvider {
    static var previews: some View {
        FoodBudgetView()
    }
}
