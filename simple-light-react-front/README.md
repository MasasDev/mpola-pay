# Mpola Pay - Simple React Frontend

A lightweight React frontend for the Mpola Pay payment scheduling system.

## Features

- ✨ Simple, clean interface
- � Create and manage customers
- �📝 Create payment schedules with multiple recipients
- 👥 View and manage existing payment schedules
- 💰 Fund payment schedules
- ⏸️ Pause/resume payment schedules
- 📱 Responsive design
- 🚫 No authentication required

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Mpola Pay backend running (default: http://localhost:8000)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables (optional):
Create a `.env` file in the root directory:
```
REACT_APP_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm start
```

The app will open at http://localhost:3000

### Building for Production

```bash
npm run build
```

## Usage

### Creating a Customer

1. Go to the "Create Customer" tab
2. Fill in customer information:
   - Email address
   - First and last name
   - Country code and phone number
3. Click "Create Customer"
4. You'll receive a Bitnob customer ID that can be used for payment schedules
5. If the customer already exists, you'll get their existing ID

### Creating a Payment Schedule

1. Go to the "Create Schedule" tab
2. Fill in customer email, title, and description
3. Select payment frequency (daily, weekly, monthly, or test mode)
4. Set the start date
5. Add recipients with their details:
   - Name and phone number
   - Country code
   - Amount per installment
   - Number of installments
6. Click "Create Payment Schedule"

### Managing Schedules

1. Go to the "View Schedules" tab
2. View all existing payment schedules
3. Fund schedules by clicking "Fund Schedule"
4. Pause/resume schedules as needed
5. Monitor funding status and payment progress

## API Integration

The frontend integrates with the Mpola Pay backend API endpoints:

- `POST /api/create-customer/` - Create a new customer
- `GET /api/payment-schedules/` - List all schedules
- `POST /api/payment-schedules/` - Create new schedule
- `POST /api/payment-schedules/{id}/fund/` - Fund a schedule
- `POST /api/payment-schedules/{id}/pause/` - Pause a schedule
- `POST /api/payment-schedules/{id}/activate/` - Activate a schedule

## Project Structure

```
src/
├── components/
│   ├── CustomerForm.js              # Form for creating customers
│   ├── PaymentScheduleForm.js       # Form for creating schedules
│   └── PaymentScheduleList.js       # List and manage schedules
├── api.js                           # API client and endpoints
├── App.js                           # Main app component
├── index.js                         # App entry point
└── index.css                        # Global styles
```

## Customization

### Styling
Edit `src/index.css` to customize the appearance. The app uses a clean, modern design with CSS Grid and Flexbox.

### API Configuration
Modify `src/api.js` to change API endpoints or add authentication headers if needed.

### Add Features
- Add new components in the `src/components/` directory
- Extend the API client in `src/api.js`
- Update the main app navigation in `src/App.js`

### Customer Workflow
The typical workflow is:
1. **Create Customer** - Register customer in Bitnob system
2. **Create Schedule** - Set up payment plan using customer email
3. **Fund Schedule** - Add money to cover payments
4. **Monitor Progress** - Track payments and funding status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Mpola Pay system.
