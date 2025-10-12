// DataScannerView.swift

import SwiftUI
import VisionKit // Apple's framework for camera vision

// This is the "bridge" from UIKit's scanner to SwiftUI
struct DataScannerView: UIViewControllerRepresentable {
    // This binding allows the view to send the scanned text back to the parent view
    @Binding var scannedText: String
    
    // This will be used to tell the parent view to dismiss the scanner
    @Environment(\.presentationMode) var presentationMode

    // Creates the underlying DataScannerViewController
    func makeUIViewController(context: Context) -> DataScannerViewController {
        let viewController = DataScannerViewController(
            recognizedDataTypes: [.text()], // We only want to look for text
            qualityLevel: .balanced,
            isHighlightingEnabled: true // Shows a yellow highlight over detected text
        )
        viewController.delegate = context.coordinator
        return viewController
    }

    // This is required but we don't need to update the view
    func updateUIViewController(_ uiViewController: DataScannerViewController, context: Context) {}

    // Creates the coordinator that handles events from the scanner
    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    // This class acts as the delegate, listening for taps and other events
    class Coordinator: NSObject, DataScannerViewControllerDelegate {
        var parent: DataScannerView

        init(parent: DataScannerView) {
            self.parent = parent
        }

        // This function is called when the user taps on a piece of detected text
        func dataScanner(_ dataScanner: DataScannerViewController, didTapOn item: RecognizedItem) {
            switch item {
            case .text(let text):
                // Get all the scanned text and join it together
                parent.scannedText = text.transcript
                
                // Tell the scanner to stop and dismiss the view
                dataScanner.stopScanning()
                parent.presentationMode.wrappedValue.dismiss()
            default:
                break
            }
        }
    }
}