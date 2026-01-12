import { MATCH_CONFIG } from "../constants";

export interface ValidationResult {
    isValid: boolean;
    errors: string[];
}

export const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

export const validatePassword = (password: string): ValidationResult => {
    const errors: string[] = [];

    if (password.length < MATCH_CONFIG.MIN_PASSWORD_LENGTH) {
        errors.push(
            `Password must be at least ${MATCH_CONFIG.MIN_PASSWORD_LENGTH} characters long`
        );
    }

    // At least one letter (uppercase or lowercase)
    if (!/[A-Za-z]/.test(password)) {
        errors.push("Password must contain at least one letter");
    }

    // At least one number
    if (!/[0-9]/.test(password)) {
        errors.push("Password must contain at least one number");
    }

    // At least one special character
    if (!/[^A-Za-z0-9]/.test(password)) {
        errors.push("Password must contain at least one special character");
    }

    return {
        isValid: errors.length === 0,
        errors,
    };
};

export const validateUsername = (username: string): ValidationResult => {
    const errors: string[] = [];

    if (username.length < 3) {
        errors.push("Username must be at least 3 characters long");
    }

    if (username.length > 30) {
        errors.push("Username must be less than 30 characters");
    }

    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
        errors.push(
            "Username can only contain letters, numbers, underscores, and hyphens"
        );
    }

    return {
        isValid: errors.length === 0,
        errors,
    };
};

export const validateCVText = (text: string): ValidationResult => {
    const errors: string[] = [];

    if (text.length < MATCH_CONFIG.MIN_CV_LENGTH) {
        errors.push(
            `CV text must be at least ${MATCH_CONFIG.MIN_CV_LENGTH} characters long`
        );
    }

    return {
        isValid: errors.length === 0,
        errors,
    };
};

export const validateJobDescription = (text: string): ValidationResult => {
    const errors: string[] = [];

    if (text.length < MATCH_CONFIG.MIN_JOB_DESC_LENGTH) {
        errors.push(
            `Job description must be at least ${MATCH_CONFIG.MIN_JOB_DESC_LENGTH} characters long`
        );
    }

    return {
        isValid: errors.length === 0,
        errors,
    };
};
