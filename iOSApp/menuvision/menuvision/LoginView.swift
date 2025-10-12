import SwiftUI

// An enum to handle the Sex selection cleanly.
enum Sex: String, CaseIterable, Identifiable {
    case female = "Female"
    case male = "Male"
    var id: Self { self }
}


struct LoginView: View {
    @Environment(\.dismiss) private var dismiss  // 👈 Add this line

    @AppStorage("isLoggedIn") private var isLoggedIn = false
    
    @State private var name: String = ""
    @State private var selectedSex: Sex = .female
    @State private var age: String = ""
    @State private var height: String = ""
    @State private var weight: String = ""

    var body: some View {
        ZStack {
            Color.appBackground.ignoresSafeArea()

            VStack(spacing: 20) {
                // --- Title ---
                HStack {
                    Image("carrotside")
                        .resizable()
                        .scaledToFit()
                        .rotationEffect(.degrees(-180))
                    Text("LOGIN")
                        .font(.custom("BudokanRounded-Bold", size: 40))
                        .foregroundColor(.appAccent)
                    Image("carrotside")
                        .resizable()
                        .scaledToFit()
                }

                // --- Form Fields ---
                VStack(alignment: .leading, spacing: 15) {
                    Text("NAME").formLabelStyle()
                    TextField("", text: $name).textFieldStyle()
                    Text("SEX").formLabelStyle()
                    SexSelector(selectedSex: $selectedSex)
                    Text("AGE").formLabelStyle()
                    TextField("", text: $age)
                        .keyboardType(.numberPad)
                        .textFieldStyle()
                    Text("HEIGHT (IN)").formLabelStyle()
                    TextField("", text: $height)
                        .keyboardType(.decimalPad)
                        .textFieldStyle()
                    Text("WEIGHT (LBS)").formLabelStyle()
                    TextField("", text: $weight)
                        .keyboardType(.decimalPad)
                        .textFieldStyle()
                }

                Spacer()

                Button(action: {
                    // save user data here if needed
                    isLoggedIn = true
                    dismiss()
                }) {
                    Text("SUBMIT")
                        .font(.custom("BudokanRounded-Bold", size: 22))
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.appAccent)
                        .cornerRadius(10)
                }
            }
            .padding(.horizontal, 30)
            .padding(.vertical, 40)
        }
    }
}


// Custom view for the Male/Female selector
struct SexSelector: View {
    @Binding var selectedSex: Sex
    
    var body: some View {
        HStack(spacing: 15) {
            Button(action: { selectedSex = .female }) {
                Text("♀")
                    

            }
            .buttonStyle(SexButtonStyle(isSelected: selectedSex == .female))
            
            Button(action: { selectedSex = .male }) {
                Text("♂️")
            }
            .buttonStyle(SexButtonStyle(isSelected: selectedSex == .male))
        }
    }
}



// Custom modifier for the text field style
struct CustomTextFieldStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .font(.custom("BudokanRounded-Bold", size: 18)) // <-- Use your font here
            .padding(12)
            .background(Color.appTextField)
            .cornerRadius(10)
            .foregroundColor(.appAccent)
    }
}

// Custom modifier for the label style
struct FormLabelStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .font(.custom("BudokanRounded-Bold", size: 20)) // <-- Use your font here
            .fontWeight(.bold)
            .foregroundColor(.appAccent)
    }
}

// Custom button style for the sex selector
struct SexButtonStyle: ButtonStyle {
    var isSelected: Bool
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding()
            .background(Color.appTextField)
            .foregroundColor(isSelected ? .appAccent : .gray.opacity(0.5))
            .cornerRadius(10)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(isSelected ? Color.appAccent : Color.clear, lineWidth: 2)
            )
    }
}

// Helper extensions to make styling easier
extension View {
    func textFieldStyle() -> some View {
        self.modifier(CustomTextFieldStyle())
    }
    
    func formLabelStyle() -> some View {
        self.modifier(FormLabelStyle())
    }
}

struct LoginView_Previews: PreviewProvider {
    static var previews: some View {
        LoginView()
    }
}
