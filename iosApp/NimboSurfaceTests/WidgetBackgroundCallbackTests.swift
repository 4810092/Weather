import Foundation
import XCTest

final class WidgetBackgroundCallbackTests: XCTestCase {
    @MainActor
    func testHandlerConstructedOnMainCanBeCalledFromBackgroundQueue() async {
        let handler = makeWidgetBackgroundEventHandler()
        let completed = expectation(description: "The system completion returns to main")
        DispatchQueue.global().async {
            // An unrelated identifier avoids creating a real background URLSession.
            handler("unrelated-session") {
                XCTAssertTrue(Thread.isMainThread)
                completed.fulfill()
            }
        }
        await fulfillment(of: [completed], timeout: 3)
    }
}
