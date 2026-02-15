import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './GameSetupModal.css';

const CAREER_OPTIONS = [
    { value: 'STUDENT_FULLY_FUNDED', label: 'Student (Fully Funded)', wealth: '₹5,000', income: '₹5,000 (Allowance)' },
    { value: 'STUDENT_PART_TIME', label: 'Student (Part Time)', wealth: '₹10,000', income: '₹8,000 (Freelance)' },
    { value: 'FRESHER', label: 'Fresher (Just Started)', wealth: '₹20,000', income: '₹25,000 (Salary)' },
    { value: 'PROFESSIONAL', label: 'Professional (Experienced)', wealth: '₹100,000', income: '₹80,000 (Salary)' },
    { value: 'BUSINESS_OWNER', label: 'Business Owner', wealth: '₹50,000', income: '₹60,000 (Business)' },
    { value: 'RETIRED', label: 'Retired', wealth: '₹500,000', income: '₹30,000 (Pension)' },
];

const RISK_OPTIONS = [
    { value: 'LOW', label: 'Low (Safe Player)' },
    { value: 'MEDIUM', label: 'Medium (Balanced)' },
    { value: 'HIGH', label: 'High (Risk Taker)' },
];

const GameSetupModal = ({ isOpen, onClose, onConfirm }) => {
    const { t } = useTranslation();
    const [formData, setFormData] = useState({
        career_stage: 'FRESHER',
        risk_appetite: 'MEDIUM',
        user_name: '',
    });

    if (!isOpen) return null;

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onConfirm(formData);
    };

    const selectedCareer = CAREER_OPTIONS.find(c => c.value === formData.career_stage);

    return (
        <div className="modal-overlay">
            <div className="setup-modal">
                <h2>{t('setup.title', 'Create Your Profile')}</h2>
                <p>{t('setup.subtitle', 'Choose your starting point in life.')}</p>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="user_name">{t('setup.name', 'Name (Optional)')}</label>
                        <input
                            type="text"
                            id="user_name"
                            name="user_name"
                            className="form-input"
                            value={formData.user_name}
                            onChange={handleChange}
                            placeholder="Enter your name"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="career_stage">{t('setup.career', 'Career Stage')}</label>
                        <select
                            id="career_stage"
                            name="career_stage"
                            className="form-select"
                            value={formData.career_stage}
                            onChange={handleChange}
                        >
                            {CAREER_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>

                        {selectedCareer && (
                            <div className="career-details">
                                <div>Starting Wealth: <strong>{selectedCareer.wealth}</strong></div>
                                <div>Monthly Income: <strong>{selectedCareer.income}</strong></div>
                            </div>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="risk_appetite">{t('setup.risk', 'Risk Appetite')}</label>
                        <select
                            id="risk_appetite"
                            name="risk_appetite"
                            className="form-select"
                            value={formData.risk_appetite}
                            onChange={handleChange}
                        >
                            {RISK_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>
                    </div>

                    <div className="modal-actions">
                        <button type="button" className="btn-cancel" onClick={onClose}>
                            {t('common.cancel', 'Cancel')}
                        </button>
                        <button type="submit" className="btn-submit">
                            {t('common.start_game', 'Start Game')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default GameSetupModal;
