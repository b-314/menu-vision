//
//  ImagePicker.swift
//  menuvision
//
//  Created by Emily Jon on 10/11/25.
//


// ImagePicker.swift

import SwiftUI

struct ImagePicker: UIViewControllerRepresentable {
    // This binding will hold the image the user captures.
    @Binding var image: UIImage?
    @Environment(\.presentationMode) var presentationMode

    // Creates the underlying camera controller.
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera // Use the camera, not the photo library.
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    // Creates the coordinator to handle events from the camera.
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    // The Coordinator class listens for when the user takes a picture.
    class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        let parent: ImagePicker

        init(_ parent: ImagePicker) {
            self.parent = parent
        }

        // This function is called when the user takes a photo.
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            // Get the captured image and assign it to our binding.
            if let uiImage = info[.originalImage] as? UIImage {
                parent.image = uiImage
            }
            // Dismiss the camera view.
            parent.presentationMode.wrappedValue.dismiss()
        }
    }
}