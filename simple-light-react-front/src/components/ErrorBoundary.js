import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <div className="card" style={{ 
          border: '2px solid #ff6b6b', 
          backgroundColor: '#ffe0e0',
          padding: '2rem',
          margin: '1rem 0'
        }}>
          <h2 style={{ color: '#d63031', marginBottom: '1rem' }}>
            🚨 Something went wrong
          </h2>
          <p style={{ color: '#2d3436', marginBottom: '1rem' }}>
            The application encountered an unexpected error. This might be due to:
          </p>
          <ul style={{ color: '#636e72', marginBottom: '1.5rem', paddingLeft: '1.5rem' }}>
            <li>Network connectivity issues</li>
            <li>Server configuration problems</li>
            <li>API service unavailability</li>
          </ul>
          
          <div style={{ marginBottom: '1.5rem' }}>
            <button 
              className="btn"
              onClick={() => window.location.reload()}
              style={{ 
                backgroundColor: '#0984e3', 
                color: 'white',
                marginRight: '1rem'
              }}
            >
              🔄 Reload Page
            </button>
            <button 
              className="btn"
              onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
              style={{ 
                backgroundColor: '#00b894', 
                color: 'white'
              }}
            >
              ↩️ Try Again
            </button>
          </div>
          
          {process.env.NODE_ENV === 'development' && (
            <details style={{ 
              backgroundColor: '#f8f9fa', 
              padding: '1rem', 
              borderRadius: '4px',
              fontSize: '0.875rem'
            }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                🐛 Technical Details (Development Only)
              </summary>
              <pre style={{ 
                marginTop: '1rem', 
                whiteSpace: 'pre-wrap',
                color: '#e17055'
              }}>
                {this.state.error && this.state.error.toString()}
              </pre>
              <pre style={{ 
                marginTop: '0.5rem',
                whiteSpace: 'pre-wrap',
                color: '#636e72',
                fontSize: '0.75rem'
              }}>
                {this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
