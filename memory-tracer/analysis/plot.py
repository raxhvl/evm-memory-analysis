import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm


def plot_normal_distribution(dataframe, column_name, output_file):
    """
    Plots the normal distribution of a specified column in a DataFrame and saves it to a file.

    Parameters:
    - dataframe: pd.DataFrame containing the data.
    - column_name: str, the name of the column for which to plot the distribution.
    - output_file: str, the file path to save the plot.
    """
    if column_name not in dataframe.columns:
        print(f"Column '{column_name}' does not exist in the DataFrame.")
        return

    # Extract the specified column
    data = dataframe[column_name]  # Drop NaN values for accurate calculations
    data = remove_outliers(data)

    # Calculate mean and standard deviation
    mean = np.mean(data)
    std_dev = np.std(data)
    print(mean, std_dev, data.mean())

    # Create a range of values for plotting the normal distribution
    x = np.linspace(mean - 4 * std_dev, mean + 4 * std_dev, 1000)

    # Use scipy to calculate the normal distribution PDF
    pdf = norm.pdf(x, mean, std_dev)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(x, pdf, label=f"Normal Distribution of {column_name}", color="blue")
    plt.title(f"Normal Distribution of {column_name}")
    plt.xlabel(column_name)
    plt.ylabel("Probability Density")

    # Highlight the 68-95-99 rule
    plt.fill_between(
        x,
        pdf,
        where=((x >= mean - std_dev) & (x <= mean + std_dev)),
        color="lightblue",
        alpha=0.5,
        label="68% (±1σ)",
    )
    plt.fill_between(
        x,
        pdf,
        where=((x >= mean - 2 * std_dev) & (x <= mean + 2 * std_dev)),
        color="lightgreen",
        alpha=0.5,
        label="95% (±2σ)",
    )
    plt.fill_between(
        x,
        pdf,
        where=((x >= mean - 3 * std_dev) & (x <= mean + 3 * std_dev)),
        color="lightyellow",
        alpha=0.5,
        label="99.7% (±3σ)",
    )

    # Mark the mean and standard deviations
    plt.axvline(mean, color="red", linestyle="--", label="Mean")
    plt.axvline(mean + std_dev, color="green", linestyle="--", label="1 Std Dev")
    plt.axvline(mean - std_dev, color="green", linestyle="--")
    plt.axvline(mean + 2 * std_dev, color="orange", linestyle="--", label="2 Std Dev")
    plt.axvline(mean - 2 * std_dev, color="orange", linestyle="--")
    plt.axvline(mean + 3 * std_dev, color="purple", linestyle="--", label="3 Std Dev")
    plt.axvline(mean - 3 * std_dev, color="purple", linestyle="--")

    plt.legend()
    plt.grid()

    # Save the plot to a file
    plt.savefig(output_file)
    plt.close()  # Close the figure


def plot_top_values(dataframe, column_name, output_file):
    """Plots the top 10 most frequent values in the specified column as relative frequencies."""
    if column_name not in dataframe.columns:
        print(f"Column '{column_name}' does not exist in the DataFrame.")
        return

    # Get the top 10 most frequent values as relative frequencies
    total_count = dataframe[column_name].count()  # Count non-NaN values
    top_values = dataframe[column_name].value_counts(normalize=True).nlargest(10)

    # Plotting
    plt.figure(figsize=(10, 6))
    top_values.plot(kind="bar", color="skyblue")
    plt.title(f"Top 10 Most Popular Values in {column_name} (Relative Frequency)")
    plt.xlabel(column_name)
    plt.ylabel("Relative Frequency")
    plt.xticks(rotation=45)
    plt.grid(axis="y")

    # Save the plot to a file
    plt.savefig(output_file)
    plt.close()


def remove_outliers(data):
    """
    Removes outliers from the data using the IQR method.

    Parameters:
    - data: pd.Series containing the data.

    Returns:
    - pd.Series with outliers removed.
    """
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1

    # Define bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Return data without outliers
    return data[(data >= lower_bound) & (data <= upper_bound)]
