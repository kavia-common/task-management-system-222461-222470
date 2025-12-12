from app import create_app

# Create app via factory to ensure proper Api initialization and config
app = create_app()

if __name__ == "__main__":
    # Bind to 0.0.0.0:3001 to match preview requirements
    app.run(host="0.0.0.0", port=3001)
