//
//  APIService.swift
//  menuvision
//
//  Created by Emily Jon on 10/12/25.
//


import Foundation

class APIService {
    // This function will send the raw text and get back the structured menu
    func processMenu(rawText: String, completion: @escaping (Result<[MenuCategory], Error>) -> Void) {
        // IMPORTANT: Use your friend's local IP address and port 8000
        guard let url = URL(string: "http://152.23.91.63:8000/process_menu_text/") else { return }
        
        var request = URLRequest(url: url, timeoutInterval: 120.0)

        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        // Create the request body
        let requestBody = ["menu_text": rawText]
        
        do {
            request.httpBody = try JSONEncoder().encode(requestBody)
        } catch {
            completion(.failure(error))
            return
        }

        // Make the network call
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let data = data else {
                // Handle case where data is nil
                return
            }
            
            // Decode the JSON response into our new Swift models
            do {
                let menuCategories = try JSONDecoder().decode([MenuCategory].self, from: data)
                completion(.success(menuCategories))
            } catch {
                print("JSON Decoding Error: \(error)")
                completion(.failure(error))
            }
        }.resume()
    }
}
