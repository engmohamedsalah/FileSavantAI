# Stage 1: Compile the C program
FROM gcc:latest AS builder
WORKDIR /app
COPY file_info.c .
RUN gcc -o file_info file_info.c

# Stage 2: Run AI tool and C program
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /app/file_info .
COPY ai_integration.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN touch hello_world.txt
CMD ["python3", "ai_integration.py"]