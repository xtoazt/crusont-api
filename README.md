# ⚔️ Crusont API

A powerful multi-provider AI gateway with multiple API key support, rustic UI, and comprehensive documentation.

## 🚀 Features

### 🔑 Multiple API Keys
- Create unlimited API keys per user
- Custom naming for easy identification
- Track usage per key
- One-click key management

### 🎨 Rustic UI Design
- Medieval/tech aesthetic with dark theme
- Responsive design for all devices
- Animated elements and smooth transitions
- Intuitive key management interface

### 🤖 Multi-Provider AI Support
- OpenAI, Anthropic, Google, and more
- Automatic provider failover
- Unified API interface
- Real-time provider health monitoring

### 📚 Comprehensive Documentation
- Complete API reference
- Code examples in multiple languages
- Interactive documentation site
- FAQ and troubleshooting guides

## 🏗️ Architecture

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - Database for users and API keys
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation and serialization

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Advanced animations and responsive design
- **HTML5** - Semantic markup and accessibility

### Deployment
- **Vercel** - Serverless deployment platform
- **8 Serverless Functions** - Optimized for performance
- **Static File Serving** - Frontend and documentation

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Home endpoint with API information
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions
- `POST /v1/moderations` - Content moderation
- `POST /v1/embeddings` - Text embeddings

### Consolidated Endpoints
- `POST /v1/audio/speech` - Text-to-speech
- `POST /v1/audio/transcriptions` - Speech-to-text
- `POST /v1/audio/translations` - Audio translation
- `POST /v1/images/generations` - Image generation
- `POST /v1/images/upscale` - Image upscaling
- `POST /v1/text/translations` - Text translation

### API Key Management
- `GET /v1/keys` - List user's API keys
- `POST /v1/keys` - Create new API key
- `DELETE /v1/keys/{key_id}` - Delete API key

## 🎯 Quick Start

### 1. Get Your API Key
```bash
# Join Discord and use the command
/user get-key

# Or use the web interface
# Visit the deployed site and create a key
```

### 2. Make Your First Request
```python
import openai

client = openai.OpenAI(
    base_url="https://api.crusont.com/v1",
    api_key="your-api-key-here",
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello, AI!"}],
)

print(response.choices[0].message.content)
```

### 3. Manage Your Keys
- Visit the web interface at `/`
- Create multiple keys for different applications
- Track usage and manage access

## 💰 Pricing Tiers

| Tier | Price | Tokens/Day | Messages/Day | IP Policy |
|------|-------|------------|--------------|-----------|
| Member | Free | 42,069 | ~200 | IP-Locked |
| Donator/Booster | $5 one-time | 300,000 | ~600 | IP-Locked |
| Contributor | Community | 325,000 | ~650 | IP-Locked |
| Subscriber | $10/month | 750,000 | ~1,200 | IP-Free |
| Premium | $25/month | 3,000,000 | ~4,000 | IP-Free |
| Enterprise | $50/month | 7,000,000 | ~10,000 | IP-Free |

## 🛠️ Development

### Local Setup
```bash
# Clone the repository
git clone https://github.com/crusont/api.git
cd api

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_URL="your-mongodb-connection-string"

# Run the development server
uvicorn api.app.main:app --reload
```

### Vercel Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables
vercel env add DB_URL
```

## 📁 Project Structure

```
crusont-api/
├── api/                    # Backend API
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Data models
│   │   ├── providers/     # AI providers
│   │   └── main.py        # FastAPI app
│   └── index.py           # Vercel entry point
├── frontend/              # Web interface
│   ├── index.html         # Main page
│   ├── styles.css         # Styling
│   └── script.js          # JavaScript
├── docs/                  # Documentation
│   ├── index.html         # Docs page
│   ├── styles.css         # Docs styling
│   └── script.js          # Docs JavaScript
├── bot/                   # Discord bot
├── vercel.json           # Vercel configuration
└── requirements.txt      # Python dependencies
```

## 🔧 Configuration

### Environment Variables
- `DB_URL` - MongoDB connection string
- `API_SECRET` - API secret key (optional)
- `RATE_LIMIT` - Rate limiting configuration (optional)

### Database Schema
- `users` - User accounts and settings
- `api_keys` - API key management
- `providers` - Provider configurations and metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Discord**: [Join our community](https://discord.gg/crusont)
- **Documentation**: [Read the docs](https://docs.crusont.com)
- **Issues**: [Report bugs](https://github.com/crusont/api/issues)

## 🎉 Acknowledgments

- Built with open-source principles
- Inspired by the AI community
- Powered by multiple AI providers
- Designed for developers, by developers

---

**From one crusont – to a journey!** ⚔️

*10B+ API requests processed • 99.9% Uptime • Built with open-source principles*