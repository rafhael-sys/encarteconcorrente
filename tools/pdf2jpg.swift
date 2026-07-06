import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

// uso: pdf2jpg <entrada.pdf> <prefixo_saida> [larguraMax=1400]
let args = CommandLine.arguments
guard args.count >= 3, let doc = CGPDFDocument(URL(fileURLWithPath: args[1]) as CFURL) else {
    FileHandle.standardError.write(Data("uso: pdf2jpg entrada.pdf prefixo_saida [largura]\n".utf8))
    exit(1)
}
let maxW: CGFloat = args.count > 3 ? CGFloat(Double(args[3]) ?? 1400) : 1400
for i in 1...doc.numberOfPages {
    guard let page = doc.page(at: i) else { continue }
    let box = page.getBoxRect(.mediaBox)
    let scale = maxW / box.width
    let w = Int(box.width * scale), h = Int(box.height * scale)
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
                              bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(),
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { continue }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: CGFloat(w), height: CGFloat(h)))
    ctx.scaleBy(x: scale, y: scale)
    ctx.translateBy(x: -box.minX, y: -box.minY)
    ctx.drawPDFPage(page)
    guard let img = ctx.makeImage() else { continue }
    let out = URL(fileURLWithPath: "\(args[2])_p\(i).jpg")
    guard let dest = CGImageDestinationCreateWithURL(out as CFURL, UTType.jpeg.identifier as CFString, 1, nil) else { continue }
    CGImageDestinationAddImage(dest, img, [kCGImageDestinationLossyCompressionQuality: 0.72] as CFDictionary)
    CGImageDestinationFinalize(dest)
    print(out.path)
}
