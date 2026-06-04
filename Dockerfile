# Stage 1: Build the application
FROM golang:alpine as builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o main .

# Stage 2: Set up the database
FROM postgres:alpine
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword
ENV POSTGRES_DB=mydb

# Stage 3: Set up the application
FROM gstack/gstack:latest
WORKDIR /app
COPY --from=builder /app/main .
COPY config.yaml .
ENV AUTH0_DOMAIN=myauth0domain
ENV AUTH0_CLIENT_ID=myauth0clientid
ENV AUTH0_CLIENT_SECRET=myauth0clientsecret
ENV GITHUB_ACTIONS_TOKEN=mygithubactionstoken
ENV PROMETHEUS_URL=myprometheusurl
EXPOSE 8080
CMD ["./main"]

# Stage 4: Set up Prometheus for monitoring
FROM prometheus/prometheus:latest
COPY prometheus.yml .