import { isAxiosError } from 'axios';

/**
 * Normalized API error response
 */
export interface NormalizedError {
    message: string;
    statusCode?: number;
    field?: string;
    details?: Record<string, string[]>;
}

/**
 * Extracts and normalizes error messages from various error types
 * Handles Axios errors, standard Error objects, and unknown error types
 */
export function normalizeApiError(error: unknown): NormalizedError {
    if (isAxiosError(error)) {
        const response = error.response;
        const statusCode = response?.status;
        const data = response?.data;

        // Handle structured error responses from Django
        if (data) {
            // Django REST framework validation errors
            if (typeof data === 'object' && !Array.isArray(data)) {
                // Check for common Django error fields
                if (data.detail) {
                    return {
                        message: String(data.detail),
                        statusCode,
                    };
                }

                if (data.message) {
                    return {
                        message: String(data.message),
                        statusCode,
                    };
                }

                // Handle field-level validation errors
                if (data.non_field_errors) {
                    return {
                        message: Array.isArray(data.non_field_errors)
                            ? data.non_field_errors.join('\n')
                            : String(data.non_field_errors),
                        statusCode,
                        details: data,
                    };
                }

                // Extract first field error if exists
                const fieldErrors = Object.entries(data).filter(
                    ([key]) => key !== 'detail' && key !== 'message'
                );

                if (fieldErrors.length > 0) {
                    const errorMessages = fieldErrors.map(([field, errors]) => {
                        const fieldName = field.replace(/_/g, ' ');
                        const errorList = Array.isArray(errors) ? errors : [errors];
                        return `${fieldName}: ${errorList.join(', ')}`;
                    });

                    return {
                        message: errorMessages.join('\n'),
                        statusCode,
                        details: data,
                    };
                }
            }

            // Plain string response
            if (typeof data === 'string') {
                return {
                    message: data,
                    statusCode,
                };
            }
        }

        // Network or timeout errors
        if (error.code === 'ECONNABORTED') {
            return {
                message: 'Request timed out. Please try again.',
                statusCode: 408,
            };
        }

        if (error.code === 'ERR_NETWORK') {
            return {
                message: 'Network error. Please check your connection.',
                statusCode: 0,
            };
        }

        // Fallback for axios errors without response data
        return {
            message: error.message || 'An unexpected error occurred',
            statusCode,
        };
    }

    // Standard Error object
    if (error instanceof Error) {
        return {
            message: error.message,
        };
    }

    // Unknown error type
    return {
        message: 'An unexpected error occurred',
    };
}

/**
 * Creates an Error object from normalized error for component state
 */
export function toError(error: unknown): Error {
    const normalized = normalizeApiError(error);
    return new Error(normalized.message);
}
