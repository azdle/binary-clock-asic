import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

@cocotb.test()
async def test_my_design(dut):
    dut._log.info("start")

    clock = Clock(dut.CLK, 1, units="ms")
    cocotb.start_soon(clock.start())

    dut.RST.value = 1
    await ClockCycles(dut.CLK, 10)
    dut.RST.value = 0

    await ClockCycles(dut.CLK, 50)

    for _ in range(0,10):
        print("vvv", dut.binary_clock.seconds.value.integer, dut.binary_clock.miliseconds.value.integer)
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
async def ms_counter_counts_ms(dut):
    dut._log.info("start")


    clock = Clock(dut.CLK, 1, units="ms")
    cocotb.start_soon(clock.start())

    dut.RST.value = 1
    await ClockCycles(dut.CLK, 1)
    dut.RST.value = 0

    for i in range(0,105):
        assert dut.binary_clock.miliseconds.value.integer == 0


        print(dut.binary_clock.seconds.value.integer,  i % 60)
        assert dut.binary_clock.seconds.value.integer  == i % 60

        await ClockCycles(dut.CLK, 99)
        print("@99", dut.binary_clock.seconds.value.integer,  i % 60)
        await ClockCycles(dut.CLK, 1)
