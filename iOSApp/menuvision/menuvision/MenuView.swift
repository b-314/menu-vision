import SwiftUI

extension Color {
    static let appBackground = Color(red: 0.82, green: 0.85, blue: 0.80)
    static let appAccent = Color(red: 0.75, green: 0.45, blue: 0.35)
    static let appTextField = Color(red: 0.96, green: 0.95, blue: 0.92)
}


struct MenuView: View {
    // State for Camera and Nutrition remains the same
    @State private var shouldNavigateToCamera = false
    @State private var shouldNavigateToNutrition = false
    @State private var shouldNavigateToFoodBudget = false

    
    // 1. Change the profile state variable to control the sheet
    @State private var isShowingProfileSheet = false

    var body: some View {
        NavigationView {
            ZStack {
                Color.appBackground.ignoresSafeArea()
                
                
                // Remove the profile link from here
                backgroundNavigationLinks
                
                VStack(spacing: 20) {
                    HStack {
                        Image("carrotside")
                            .resizable()
                            .scaledToFit()
                            .rotationEffect(.degrees(-180))
                        Text("MENU VISION")
                            .multilineTextAlignment(.center)
                            .font(.custom("BudokanRounded-Bold", size: 40))
                            .foregroundColor(.appAccent)
                        Image("carrotside")
                            .resizable()
                            .scaledToFit()
                    }
                    // ... Title HStack and other buttons remain the same ...
                    
                    Button(action: { self.shouldNavigateToCamera = true }) {
                        MenuButtonStyle(iconName: "camera.fill", text: "Scan Menu", color: .blue)
                    }
                     
                    // 2. This button now toggles the sheet's state variable
                    Button(action: { self.isShowingProfileSheet = true }) {
                        MenuButtonStyle(iconName: "person.fill", text: "My Profile", color: .green)
                    }
                     
                    Button(action: { self.shouldNavigateToNutrition = true }) {
                        MenuButtonStyle(iconName: "leaf.fill", text: "Preferences", color: .orange)
                    }
                    
                    Button(action: { self.shouldNavigateToFoodBudget = true }) {
                        MenuButtonStyle(iconName: "creditcard.fill", text: "Budget", color: .red)
                    }
                    
                    Spacer()
                }
                .padding(.horizontal, 30)
                .padding(.top, 40)
            }
            .overlay(Image("sidebunny").bunnyStyle())
            .navigationBarHidden(true)
            
            // 3. Attach the sheet modifier here. It will present when the state is true.
            .sheet(isPresented: $isShowingProfileSheet) {
                // The view to present modally
                // Assuming LoginView is your profile editor
                LoginView()
            }
        }
    }
    
    // This subview no longer needs the profile link
    private var backgroundNavigationLinks: some View {
        VStack {
            NavigationLink(destination: CameraView(), isActive: $shouldNavigateToCamera) { EmptyView() }
            NavigationLink(destination: NutritionView(), isActive: $shouldNavigateToNutrition) { EmptyView() }
            NavigationLink(destination: FoodBudgetView(), isActive: $shouldNavigateToFoodBudget) { EmptyView() }
        }
    }
}

// --- MenuButtonStyle (No changes needed) ---
struct MenuButtonStyle: View {
    let iconName: String, text: String, color: Color
    var body: some View {
        HStack(spacing: 20) {
            Image(systemName: iconName).font(.title2).foregroundColor(color)
            Text(text).font(.custom("BudokanRounded-Bold", size: 22)).fontWeight(.bold).foregroundColor(.appAccent)
            Spacer()
        }
        .padding().background(Color.appTextField).cornerRadius(15).shadow(radius: 3, y: 3)
    }
}

// MARK: - Custom Modifiers for Cleaner Code
extension Image {
    func themed() -> some View {
        self.resizable().scaledToFit().frame(width: 40, height: 40).foregroundColor(.appAccent)
    }
    func bunnyStyle() -> some View {
        self.resizable().scaledToFit().frame(height: 200).allowsHitTesting(false)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .bottom)
    }
}

extension Text {
    func themedTitle() -> some View {
        self.font(.custom("BudokanRounded-Bold", size: 40)).fontWeight(.bold).foregroundColor(.appAccent)
    }
}

// MARK: - Preview
struct MenuView_Previews: PreviewProvider {
    static var previews: some View {
        MenuView()
    }
}
