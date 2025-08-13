from fastapi import FastAPI

app = FastAPI(title="AetherionGenesis API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/onboarding/hints")
def onboarding_hints():
    # Placeholder: return AI-generated steps later
    return {
        "steps": [
            "Create embedded wallet with social login",
            "Bridge starter funds to target chain",
            "Mint identity SBT",
            "Show first DeFi action"
        ]
    }
