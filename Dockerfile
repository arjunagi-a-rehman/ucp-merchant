# Use a slim Python image
FROM python:3.12-slim

# Install curl to get the uv installer
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# Copy the rest of the application
COPY . .

# Expose the API port
EXPOSE 8000

# Start the uvicorn server using uv run
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
