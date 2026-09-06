import Foundation
import NimboShared

/// Kotlin callbacks may arrive on a worker thread. The store owns synchronization;
/// this adapter deliberately has no MainActor isolation.
final class WidgetRefreshBridgeAdapter: NSObject, WidgetRefreshBridge {
    func exchange(request: String) -> String {
        let response = WidgetRefreshStore.shared.exchange(request)
        if let command = try? JSONSerialization.jsonObject(with: Data(request.utf8)) as? [String: Any],
           let result = try? JSONSerialization.jsonObject(with: Data(response.utf8)) as? [String: Any],
           (command["op"] as? String == "publish" && result["ok"] as? Bool == true) ||
            (command["op"] as? String == "configure" && result["revision"] != nil) {
            NotificationCenter.default.post(name: Notification.Name("NimboWeatherDidUpdate"), object: nil)
        }
        return response
    }
}
