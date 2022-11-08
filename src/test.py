import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

# Asserts the reset pin for 1 millisecond, not taking any clocks
async def reset(reset_wire):
    reset_wire.value = 1
    await Timer(1, units="ms")
    reset_wire.value = 0
    reset_wire._log.debug("Reset complete")

# Create an indexable list of bits from a binstr
def bit_list(s):
    bits = list(s)
    bits.reverse()
    bits = list(map(lambda b: int(b), bits))
    return bits

@cocotb.test()
async def second_counter_counts_seconds(dut):
    dut._log.info("start")

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut.RST)

    # TODO: increase range, was 1001
    for i in range(0,100):
        await ClockCycles(dut.CLK, 1)
        assert dut.binary_clock.seconds.value.integer  == i % 60
        await ClockCycles(dut.CLK, 99)
        assert dut.binary_clock.seconds.value.integer  == i % 60

@cocotb.test()
async def verify_multiplexing_output(dut):
    dut._log.info("start")

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut.RST)

    # check the output for every minute of an hour
    for current_minute in range(0, 60 + 1):
        # wait for wanted minute
        current_minute = current_minute % 60
        while True:
            await ClockCycles(dut.CLK, 100)
            if dut.binary_clock.minutes.value.integer == current_minute:
                break

        await ClockCycles(dut.CLK, 1)
        assert dut.binary_clock.minutes.value.integer == current_minute

        plex = [[0,0,0,0],
                [0,0,0,0],
                [0,0,0,0],
                [0,0,0,0]]

        for _ in range(0,4):
            pins = bit_list(dut.out.value.binstr)
            col = pins[0:4]
            row = pins[4:8]

            #print("pins", pins, col, row)

            assert sum(row) == 3

            row = row[0] == 0 and 0 or row[1] == 0 and 1 or row[2] == 0 and 2 or row[3] == 0 and 3

            for ci, cv in enumerate(col):
                #print(ci, cv)
                plex[row][ci] = cv

            await ClockCycles(dut.CLK, 1)

        #print("pat:", ("_" * 5) + ("h" * 5) + ("m" * 6))
        #print("inp:", dut.binary_clock.pixels.value.binstr)

        flat_plex = [str(pixel) for row in plex for pixel in row]
        flat_plex.reverse()
        str_plex = "".join(flat_plex)

        #print("out:", str_plex)

        assert str_plex == dut.binary_clock.pixels.value.binstr
