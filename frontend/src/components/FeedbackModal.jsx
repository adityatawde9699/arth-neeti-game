import React from 'react';

const FeedbackModal = ({ feedback, wasRecommended, onContinue }) => {
    return (
        <div className="feedback-overlay" onClick={onContinue}>
            <div className="feedback-card" onClick={(e) => e.stopPropagation()}>
                <div className={`feedback-icon ${wasRecommended ? 'good' : 'bad'}`}>
                    {wasRecommended ? '✅' : '⚠️'}
                </div>

                <h3 className="feedback-title">
                    {wasRecommended ? 'Smart Choice!' : 'Think About It...'}
                </h3>

                <div className="feedback-tip">
                    <div className="feedback-tip-label">💡 Financial Tip</div>
                    <p className="feedback-text">{feedback}</p>
                </div>

                <button className="btn btn-primary btn-block" onClick={onContinue}>
                    Continue →
                </button>
            </div>
        </div>
    );
};

export default FeedbackModal;
