const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");
const cliProgress = require("cli-progress");

const KB = 1024;
const MB = 1024 * KB;

// Config
const startMemory = 0;
const maxMemory = 100 * MB;
const step = 100 * KB;

// Path to the Go benchmark executable
const goTestPath = "";

// Function to run the benchmark and return the result
const runBenchmark = (memStart) => {
  return new Promise((resolve, reject) => {
    exec(
      `go test -bench=BenchmarkOpMstore -memStart=${memStart} ${goTestPath}`,
      (error, stdout, stderr) => {
        if (error) {
          return reject(`Error: ${stderr || error.message}`);
        }
        resolve(stdout);
      }
    );
  });
};

// Function to parse benchmark results
const parseResults = (output, memStart) => {
  const lines = output.split("\n");
  const resultLines = lines.filter((line) =>
    line.includes("BenchmarkOpMstore")
  );

  return resultLines.map((line) => {
    const parts = line.split(/\s+/);
    return {
      memory: memStart,
      iterations: parseInt(parts[1]),
      nsPerOp: parseFloat(parts[2]),
    };
  });
};

// Main function to execute benchmarks and save results
const main = async () => {
  const totalIterations = Math.ceil((maxMemory - startMemory) / step) + 1;

  // Create a new progress bar instance and use shades_classic theme
  const progressBar = new cliProgress.SingleBar(
    {
      format:
        "Benchmark Progress |{bar}| {percentage}% || {value}/{total} MemStart={memStart}",
      barCompleteChar: "\u2588",
      barIncompleteChar: "\u2591",
      hideCursor: true,
    },
    cliProgress.Presets.shades_classic
  );

  progressBar.start(totalIterations, 0);

  // Create a writable stream to write to CSV file incrementally
  const csvStream = fs.createWriteStream(
    path.join(__dirname, "out/benchmark_results.csv")
  );
  csvStream.write("offset,memory_size, iterations,nsPerOp\n"); // Write the header

  for (
    let memStart = startMemory, index = 0;
    memStart <= maxMemory;
    memStart += step, index++
  ) {
    console.log(`Running benchmark with memStart=${memStart}`);
    try {
      const output = await runBenchmark(memStart);
      const parsedResults = parseResults(output, memStart);

      // Write each result to the CSV file
      parsedResults.forEach((result) => {
        const line = `${result.memory},${result.memory + 32},${
          result.iterations
        },${result.nsPerOp}\n`;
        csvStream.write(line);
      });
    } catch (error) {
      console.error(`Failed for memStart=${memStart}: ${error}`);
    }

    progressBar.update(index + 1);
  }

  progressBar.stop();
  csvStream.end(); // Close the writable stream

  console.log("Benchmark results saved to benchmark_results.csv");
};

// Run the script
main();
