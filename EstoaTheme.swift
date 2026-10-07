
import SwiftUI

enum EstoaTheme {
    static let background = Color(red: 0.018, green: 0.045, blue: 0.072)
    static let surface = Color.white.opacity(0.065)
    static let surfaceStrong = Color.white.opacity(0.095)
    static let line = Color.cyan.opacity(0.28)
    static let active = Color.cyan
    static let flood = Color(red: 0.12, green: 0.86, blue: 0.70)
    static let ebb = Color(red: 1.00, green: 0.25, blue: 0.32)
    static let slack = Color.white
    static let secondary = Color.white.opacity(0.62)

    static let cardRadius: CGFloat = 20
    static let pagePadding: CGFloat = 16
}

struct EstoaCard<Content: View>: View {
    @ViewBuilder var content: Content
    var body: some View {
        content
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(EstoaTheme.surface, in: RoundedRectangle(cornerRadius: EstoaTheme.cardRadius))
            .overlay(RoundedRectangle(cornerRadius: EstoaTheme.cardRadius)
                .stroke(EstoaTheme.line, lineWidth: 0.7))
    }
}

struct EstoaBrandHeader: View {
    var body: some View {
        HStack(alignment:.top) {
            VStack(alignment:.leading,spacing:0) {
                Text("ESTOA")
                    .font(.system(size:34,weight:.medium,design:.serif))
                    .tracking(7).foregroundStyle(.white)
                Text("CORRIENTES Y MAREAS")
                    .font(.caption).tracking(2.2).foregroundStyle(EstoaTheme.secondary)
                Text("PATAGONIA · CHILE")
                    .font(.system(size:8,weight:.medium)).tracking(1.8)
                    .foregroundStyle(EstoaTheme.secondary)
            }
            Spacer()
            VStack(alignment:.trailing,spacing:2) {
                Text("EDICIÓN 2026").font(.caption2).bold()
                Text("Motor hidrográfico").font(.caption2)
            }.foregroundStyle(EstoaTheme.secondary)
        }
    }
}
