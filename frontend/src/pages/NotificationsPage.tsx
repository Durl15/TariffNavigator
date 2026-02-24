import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getNotifications,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  type Notification,
} from '../services/api'
import Navigation from '../components/Navigation'
import '../styles/NotificationsPage.css'

const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [unreadCount, setUnreadCount] = useState(0)
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [selectedType, setSelectedType] = useState<string>('')
  const navigate = useNavigate()

  const pageSize = 20

  // Fetch notifications
  const fetchNotifications = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getNotifications(
        page,
        pageSize,
        unreadOnly,
        selectedType || undefined
      )
      setNotifications(data.notifications)
      setTotalPages(Math.ceil(data.total / pageSize))
      setUnreadCount(data.unread_count || 0)
    } catch (err: any) {
      setError(err.message || 'Failed to load notifications')
    } finally {
      setLoading(false)
    }
  }

  // Fetch on mount and when filters change
  useEffect(() => {
    fetchNotifications()
  }, [page, unreadOnly, selectedType])

  // Handle mark as read
  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await markAsRead(notificationId)
      fetchNotifications()
    } catch (err: any) {
      setError('Failed to mark as read')
    }
  }

  // Handle mark all as read
  const handleMarkAllAsRead = async () => {
    try {
      await markAllAsRead()
      fetchNotifications()
    } catch (err: any) {
      setError('Failed to mark all as read')
    }
  }

  // Handle delete
  const handleDelete = async (notificationId: string) => {
    if (!confirm('Are you sure you want to delete this notification?')) {
      return
    }

    try {
      await deleteNotification(notificationId)
      fetchNotifications()
    } catch (err: any) {
      setError('Failed to delete notification')
    }
  }

  // Handle notification click
  const handleNotificationClick = async (notification: Notification) => {
    // Mark as read if unread
    if (!notification.is_read) {
      await handleMarkAsRead(notification.id)
    }

    // Navigate if link exists
    if (notification.link) {
      navigate(notification.link)
    }
  }

  // Format date
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    })
  }

  // Get notification icon
  const getNotificationIcon = (type: string): string => {
    switch (type) {
      case 'rate_change':
        return '📊'
      case 'deadline':
        return '⏰'
      case 'new_program':
        return '🎉'
      default:
        return '📬'
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/';
  };

  const isAuthenticated = !!localStorage.getItem('auth_token');

  return (
    <>
      <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      <div className="notifications-page">
        <div className="notifications-container">
        <div className="notifications-header">
          <h1>Notifications</h1>
          {unreadCount > 0 && (
            <button
              className="mark-all-read-button"
              onClick={handleMarkAllAsRead}
            >
              Mark All as Read
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="notifications-filters">
          <div className="filter-group">
            <label className="filter-checkbox">
              <input
                type="checkbox"
                checked={unreadOnly}
                onChange={(e) => {
                  setUnreadOnly(e.target.checked)
                  setPage(1)
                }}
              />
              <span>Unread only ({unreadCount})</span>
            </label>
          </div>

          <div className="filter-group">
            <label htmlFor="type-filter">Type:</label>
            <select
              id="type-filter"
              value={selectedType}
              onChange={(e) => {
                setSelectedType(e.target.value)
                setPage(1)
              }}
            >
              <option value="">All Types</option>
              <option value="rate_change">Rate Changes</option>
              <option value="deadline">Deadlines</option>
              <option value="new_program">New Programs</option>
            </select>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading notifications...</p>
          </div>
        ) : (
          <>
            {/* Notifications List */}
            {notifications.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📭</div>
                <h3>No notifications</h3>
                <p>
                  {unreadOnly
                    ? 'You have no unread notifications'
                    : 'You haven\'t received any notifications yet'}
                </p>
              </div>
            ) : (
              <div className="notifications-list">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`notification-card ${
                      !notification.is_read ? 'unread' : ''
                    }`}
                  >
                    <div className="notification-icon">
                      {getNotificationIcon(notification.type)}
                    </div>

                    <div
                      className="notification-body"
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <div className="notification-header-row">
                        <h3 className="notification-title">
                          {notification.title}
                        </h3>
                        {!notification.is_read && (
                          <span className="unread-badge">New</span>
                        )}
                      </div>

                      <p className="notification-message">
                        {notification.message}
                      </p>

                      <div className="notification-meta">
                        <span className="notification-date">
                          {formatDate(notification.created_at)}
                        </span>
                        {notification.link && (
                          <span className="notification-link-indicator">
                            Click to view details →
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="notification-actions">
                      {!notification.is_read && (
                        <button
                          className="action-button"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleMarkAsRead(notification.id)
                          }}
                          title="Mark as read"
                        >
                          <svg
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        </button>
                      )}
                      <button
                        className="action-button delete"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(notification.id)
                        }}
                        title="Delete"
                      >
                        <svg
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="pagination-button"
                >
                  Previous
                </button>

                <span className="pagination-info">
                  Page {page} of {totalPages}
                </span>

                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="pagination-button"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
    </>
  )
}

export default NotificationsPage
