import SwiftUI
import Vision

struct CameraView: View {
    // State variables
    @State private var capturedImage: UIImage?
    @State private var isShowingImagePicker = false
    @State private var recognizedText = ""
    @State private var isLoading = false
    @State private var showResults = false
    
    var body: some View {
        ZStack {
            // 1. Apply the custom background color
            Color.appBackground.ignoresSafeArea()
            
            VStack {
                // --- Step 3: Show Recognized Text for Confirmation ---
                if !recognizedText.isEmpty {
                    Text("Confirm Text")
                        .formTitleStyle()
                    
                    ScrollView {
                        Text(recognizedText)
                            .font(.custom("BudokanRounded-Bold", size: 16))
                            .padding()
                            .foregroundColor(.appAccent.opacity(0.8))
                    }
                    .background(Color.appTextField)
                    .cornerRadius(15)
                    .padding(.horizontal)
                    
                    HStack {
                        // Retake Button (now available on confirm screen)
                        Button(action: { self.isShowingImagePicker = true }) {
                            Text("Retake")
                                .appButtonStyle(backgroundColor: .gray)
                        }
                        // Confirm Button
                        Button(action: sendToBackend) {
                            Text("Confirm & Analyze")
                                .appButtonStyle(backgroundColor: .green)
                        }
                    }
                    .padding()
                    
                    // --- Step 2: Show Captured Image Preview ---
                } else if let image = capturedImage {
                    Text("Happy with your photo?")
                        .formTitleStyle()
                    
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFit()
                        .cornerRadius(15)
                        .padding()
                    
                    HStack {
                        Button(action: { self.isShowingImagePicker = true }) {
                            Text("Retake Photo")
                                .appButtonStyle(backgroundColor: .gray)
                        }
                        
                        Button(action: recognizeTextFromImage) {
                            Text("Analyze Text")
                                .appButtonStyle(backgroundColor: .blue)
                        }
                    }
                    .padding()
                    
                    // --- Step 1: Initial View ---
                } else {
                    Spacer()
                    Image("standbunny") // Using your bunny image
                        .resizable()
                        .scaledToFit()
                        .frame(height: 150)
                    
                    Text("Capture a clear, well-lit photo of the menu.")
                        .formTitleStyle()
                        .multilineTextAlignment(.center)
                    
                    Button(action: { self.isShowingImagePicker = true }) {
                        HStack {
                            Image(systemName: "camera.fill")
                            Text("Open Camera")
                        }
                        .appButtonStyle(backgroundColor: Color.appAccent)
                    }
                    .padding()
                    Spacer()
                }
            }
            .navigationBarHidden(true) // Hide nav bar to match theme
            .fullScreenCover(isPresented: $isShowingImagePicker) {
                ImagePicker(image: $capturedImage)
            }
            
            // Themed Loading Overlay
            if isLoading {
                ZStack {
                    Color.black.opacity(0.75).ignoresSafeArea()
                    VStack(spacing: 20) {
                        Image("TeteWalkCycle")
                            .resizable()
                            .scaledToFit()
                            .allowsHitTesting(false)
                            .frame(width: 100)
                            .scaleEffect(isLoading ? 1.1 : 1.0)
                            .animation(Animation.easeInOut(duration: 1.0).repeatForever(autoreverses: true), value: isLoading)

                        
                        Text("Analyzing...")
                            .font(.custom("BudokanRounded-Bold", size: 24))
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                    }
                }
            }
            
            // --- Update your NavigationLink ---
            NavigationLink(
                destination: ResultsView(menuData: menuCategories), // Pass the data
                isActive: $showResults
            ) {
                EmptyView()
            }
        }
    }
    
    // --- Function Flow (No changes needed here) ---
    private func recognizeTextFromImage() {
        // 1. Ensure we have an image to work with.
        guard let cgImage = capturedImage?.cgImage else {
            print("Error: capturedImage is nil.")
            return
        }
        
        isLoading = true
        
        // 2. Create a request to recognize text.
        let request = VNRecognizeTextRequest { (request, error) in
            // 3. Jump back to the main thread to update the UI.
            DispatchQueue.main.async {
                // Check for errors first.
                if let error = error {
                    print("Text recognition error: \(error.localizedDescription)")
                    isLoading = false
                    return
                }
                
                // Check that we got results.
                guard let observations = request.results as? [VNRecognizedTextObservation] else {
                    print("Error: Could not get observation results.")
                    isLoading = false
                    return
                }
                
                // Extract the text.
                let recognizedStrings = observations.compactMap { observation in
                    observation.topCandidates(1).first?.string
                }
                
                // Check if any text was actually found.
                if recognizedStrings.isEmpty {
                    print("Result: No text found in the image.")
                    // TODO: You could show an alert to the user here.
                    isLoading = false
                    return // Stay on the image preview screen.
                }
                
                // 4. Success! Update the UI to show the confirmation screen.
                print("Success! Recognized \(recognizedStrings.count) lines of text.")
                self.recognizedText = recognizedStrings.joined(separator: "\n")
                self.isLoading = false
            }
        }
        
        request.recognitionLevel = .accurate
        
        // 5. Perform the request on a background thread.
        DispatchQueue.global(qos: .userInitiated).async {
            let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
            do {
                try handler.perform([request])
            } catch {
                // If the handler itself fails, print the error.
                print("Failed to perform Vision request: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    isLoading = false
                }
            }
        }
    }
    // In CameraView.swift

    // Create an instance of your service
    private let apiService = APIService()

    // Hold the results to pass to the next screen
    @State private var menuCategories: [MenuCategory] = []

    // --- Updated sendToBackend function ---
    private func sendToBackend() {
        isLoading = true
        
        apiService.processMenu(rawText: recognizedText) { result in
            DispatchQueue.main.async {
                isLoading = false
                switch result {
                case .success(let categories):
                    self.menuCategories = categories
                    self.showResults = true // This will trigger navigation
                case .failure(let error):
                    print("API Error: \(error.localizedDescription)")
                    // TODO: Show an error alert to the user
                }
            }
        }
    }
}

// MARK: - New Custom Style Modifiers
// Add these to the bottom of your file, or to a new "Styles" file.

struct FormTitleStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .font(.custom("BudokanRounded-Bold", size: 24))
            .fontWeight(.bold)
            .foregroundColor(.appAccent)
            .padding()
    }
}

struct AppButtonStyle: ViewModifier {
    let backgroundColor: Color
    
    func body(content: Content) -> some View {
        content
            .font(.custom("BudokanRounded-Bold", size: 18))
            .fontWeight(.bold)
            .padding()
            .frame(maxWidth: .infinity)
            .background(backgroundColor)
            .foregroundColor(.white)
            .cornerRadius(15)
            .shadow(radius: 3, y: 3)
    }
}

extension View {
    func formTitleStyle() -> some View {
        self.modifier(FormTitleStyle())
    }
    
    func appButtonStyle(backgroundColor: Color) -> some View {
        self.modifier(AppButtonStyle(backgroundColor: backgroundColor))
    }
}



