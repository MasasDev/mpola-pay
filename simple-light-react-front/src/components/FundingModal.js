import React, { useState, useEffect, useRef } from 'react';
import QRCode from 'qrcode';
import './FundingModal.css';

const FundingModal = ({ isOpen, onClose, fundingData, scheduleTitle }) => {
  const [copied, setCopied] = useState(false);
  const qrCodeRef = useRef(null);

  useEffect(() => {
    if (isOpen && fundingData?.funding_details?.deposit_address && qrCodeRef.current) {
      // Clear any existing QR code
      qrCodeRef.current.innerHTML = '';
      
      // Generate QR code
      QRCode.toCanvas(qrCodeRef.current, fundingData.funding_details.deposit_address, {
        width: 200,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#ffffff'
        }
      }, (error) => {
        if (error) {
          console.error('QR Code generation error:', error);
          // Fallback: show text if QR generation fails
          qrCodeRef.current.innerHTML = `<div style="padding: 20px; text-align: center; border: 1px dashed #ccc;">QR Code generation failed</div>`;
        }
      });
    }
  }, [isOpen, fundingData]);

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy text: ', err);
      }
      document.body.removeChild(textArea);
    }
  };

  if (!isOpen || !fundingData) return null;

  const details = fundingData.funding_details;
  // const instructions = fundingData.instructions; // Currently unused
  // const scheduleInfo = fundingData.schedule_info; // Currently unused

  return (
    <div className="funding-modal-overlay" onClick={onClose}>
      <div className="funding-modal" onClick={(e) => e.stopPropagation()}>
        <div className="funding-modal-header">
          <h2>Fund Payment Schedule</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        <div className="funding-modal-content">
          <div className="schedule-info">
            <h3>"{scheduleTitle}"</h3>
            <div className="funding-summary">
              <div className="summary-item">
                <span className="label">Required Amount:</span>
                <span className="value">{details.usdt_required} USDT</span>
              </div>
              <div className="summary-item">
                <span className="label">Network:</span>
                <span className="value">{details.network}</span>
              </div>
              <div className="summary-item">
                <span className="label">UGX Equivalent:</span>
                <span className="value">{new Intl.NumberFormat().format(details.ugx_amount)} UGX</span>
              </div>
            </div>
          </div>

          <div className="deposit-section">
            <div className="qr-section">
              <h4>Scan QR Code</h4>
              <div className="qr-code-container">
                <div ref={qrCodeRef} className="qr-code"></div>
              </div>
              <p className="qr-note">Scan with your wallet app</p>
            </div>

            <div className="address-section">
              <h4>Deposit Address</h4>
              <div className="address-container">
                <div className="address-display">
                  <code className="address-text">{details.deposit_address}</code>
                  <button 
                    className={`copy-button ${copied ? 'copied' : ''}`}
                    onClick={() => copyToClipboard(details.deposit_address)}
                  >
                    {copied ? '✓ Copied!' : 'Copy'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="instructions-section">
            <h4>Instructions</h4>
            <div className="instruction-steps">
              <div className="step">
                <span className="step-number">1</span>
                <div className="step-content">
                  <strong>Send exactly {details.usdt_required} USDT</strong>
                  <p>to the address above</p>
                </div>
              </div>
              <div className="step">
                <span className="step-number">2</span>
                <div className="step-content">
                  <strong>Use {details.network} network</strong>
                  <p>{details.network === 'TRON' ? '(TRC20)' : details.network === 'ETHEREUM' ? '(ERC20)' : `(${details.network})`}</p>
                </div>
              </div>
              <div className="step">
                <span className="step-number">3</span>
                <div className="step-content">
                  <strong>Wait for confirmation</strong>
                  <p>Usually takes 1-5 minutes</p>
                </div>
              </div>
              <div className="step">
                <span className="step-number">4</span>
                <div className="step-content">
                  <strong>Schedule activates automatically</strong>
                  <p>When funds are confirmed</p>
                </div>
              </div>
            </div>
          </div>

          <div className="warning-section">
            <div className="warning-box">
              <strong>⚠️ IMPORTANT WARNINGS:</strong>
              <ul>
                <li>Make sure to use the correct <strong>{details.network}</strong> network</li>
                <li>Send exactly <strong>{details.usdt_required} USDT</strong> (not more, not less)</li>
                <li>Only send USDT to this address</li>
                <li>Double-check the address before sending</li>
              </ul>
            </div>
          </div>

          <div className="reference-section">
            <div className="reference-info">
              <span className="label">Reference ID:</span>
              <code className="reference-id">{details.reference}</code>
              <button 
                className="copy-button-small"
                onClick={() => copyToClipboard(details.reference)}
              >
                Copy
              </button>
            </div>
          </div>
        </div>

        <div className="funding-modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
          <button 
            className="btn-primary"
            onClick={() => copyToClipboard(details.deposit_address)}
          >
            Copy Address & Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default FundingModal;
