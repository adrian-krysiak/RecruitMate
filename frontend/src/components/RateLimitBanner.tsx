import { memo } from 'react';
import { type RateLimitInfo } from '../utils/rateLimitManager';
import { RateLimitManager } from '../utils/rateLimitManager';

interface RateLimitBannerProps {
    rateLimitInfo: RateLimitInfo;
    onRetry?: () => void;
}

export const RateLimitBanner = memo(({ rateLimitInfo, onRetry }: RateLimitBannerProps) => {
    const waitMessage = RateLimitManager.getWaitMessage(rateLimitInfo);
    const timeUntilReset = RateLimitManager.getTimeUntilReset(rateLimitInfo.resetTime);

    return (
        <div
            style={{
                padding: '1rem',
                marginBottom: '1rem',
                backgroundColor: '#fff3cd',
                border: '1px solid #ffc107',
                borderRadius: '4px',
                color: '#856404',
            }}
            role="alert"
            aria-live="polite"
        >
            <strong>Rate Limited</strong>
            <p style={{ margin: '0.5rem 0 0' }}>
                {waitMessage}
            </p>
            <p style={{ margin: '0.5rem 0 0', fontSize: '0.9em' }}>
                Resets in {timeUntilReset} seconds
            </p>
            {onRetry && (
                <button
                    onClick={onRetry}
                    style={{
                        marginTop: '0.5rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: '#ffc107',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                    }}
                    disabled={timeUntilReset > 0}
                    aria-label="Retry request"
                >
                    {timeUntilReset > 0 ? `Retry in ${timeUntilReset}s` : 'Retry Now'}
                </button>
            )}
        </div>
    );
});

RateLimitBanner.displayName = 'RateLimitBanner';
