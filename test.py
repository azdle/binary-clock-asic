import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

# Asserts the reset pin for 1 millisecond, not taking any clocks
async def reset(reset_wire):
    reset_wire.value = 1
    await Timer(1, units="ms")
    reset_wire.value = 0
    reset_wire._log.debug("Reset complete")

@cocotb.test()
async def test_my_design(dut):
    dut._log.info("start")

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut.RST)

    await ClockCycles(dut.CLK, 50)

    for _ in range(0,10):
        print("vvv", dut.binary_clock.seconds.value.integer, dut.binary_clock.centiseconds.value.integer)
        print(dut.out.value.binstr)
        await ClockCycles(dut.CLK, 48)
        print(dut.out.value.binstr)
        await ClockCycles(dut.CLK, 1)
        print(dut.out.value.binstr)
        await ClockCycles(dut.CLK, 1)
        print("---")
        print(dut.out.value.binstr)
        await ClockCycles(dut.CLK, 1)
        print(dut.out.value.binstr)
        await ClockCycles(dut.CLK, 1)
        print(dut.out.value.binstr)
        await ClockCycles(dut.CLK, 48)
        print("^^^", dut.binary_clock.seconds.value.integer)

@cocotb.test()
async def second_counter_counts_seconds(dut):
    dut._log.info("start")

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut.RST)

    for i in range(0,1001):
        await ClockCycles(dut.CLK, 1)
        assert dut.binary_clock.seconds.value.integer  == i % 60
        await ClockCycles(dut.CLK, 99)
        assert dut.binary_clock.seconds.value.integer  == i % 60
