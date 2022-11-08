`default_nettype none
`timescale 1ms/1ms

module tb (
  input CLK,
  input RST,
  output [7:0] out
);

    initial begin
        $dumpfile ("tb.vcd");
        $dumpvars (0, tb);
        #1;
    end

    wire [7:0] in = {6'b0, CLK, RST};

    azdle_binary_clock binary_clock (
        .io_out(out),
	.io_in(in)
    );

endmodule
