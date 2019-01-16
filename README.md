# JPEG-Encoder-Decoder

## Encoder part
- reads raw data from a PPM image
- converts the RGB pixels to YUV pixels
- divides into 8x8 Y blocks and 4x4 U and V blocks (4:2:0 subsampling)
- performs Forward DCT (Discrete Cosine Transform) and then Quantization on an 8x8 pixels block
![quantization encoder](https://raw.githubusercontent.com/vanpana/JPEG-Encoder-Decoder/master/q_encoder.png)
- performs Entropy Encoding (only ZigZag parsing and run-length encoding, NOT Huffman encoding)
![zig zag traversal](https://raw.githubusercontent.com/vanpana/JPEG-Encoder-Decoder/master/zigzag.png)
- computes output entropy

## Decoder part
- outputs the lists of 8x8 blocks of quatized Y/Cb/Cr coefficients
- DeQuantization phase - takes as input an 8x8 quantized block produced by the encoder and it multiplies this block (component-by-component) with the 8x8 quantization matrix
- starting from a list of 8x8 Y-values blocks and subsampled 4x4 U- and V-values blocks it composes the final PPM image 
