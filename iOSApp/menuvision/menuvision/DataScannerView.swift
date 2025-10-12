import SwiftUI
import VisionKit

struct DataScannerView: UIViewControllerRepresentable {
    @Binding var scannedText: String

    func makeUIViewController(context: Context) -> DataScannerViewController {
        let viewController = DataScannerViewController(
            recognizedDataTypes: [.text()],
            qualityLevel: .balanced,
            recognizesMultipleItems: false, // More focused scanning
            isHighlightingEnabled: true
        )
        
        viewController.delegate = context.coordinator
        
        // This line is crucial to start the camera session
        try? viewController.startScanning()
        
        return viewController
    }

    func updateUIViewController(_ uiViewController: DataScannerViewController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    class Coordinator: NSObject, DataScannerViewControllerDelegate {
        var parent: DataScannerView

        init(parent: DataScannerView) {
            self.parent = parent
        }

        // This function is called when the user taps on a piece of highlighted text
        func dataScanner(_ dataScanner: DataScannerViewController, didTapOn item: RecognizedItem) {
            switch item {
            case .text(let text):
                parent.scannedText = text.transcript
                // We stop scanning after the first successful tap
                dataScanner.stopScanning()
            default:
                break
            }
        }
    }
}
