import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Bell,
  TrendingUp,
  Clock,
  Zap,
  Check,
  Trash2,
} from 'lucide-react'
import {
  getNotifications,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  type Notification,
} from '../services/api'
import Navigation from '../components/Navigation'
import { usePageTitle } from '../hooks/usePageTitle'

const NotificationsPage: React.FC = () => {
  usePageTitle('Notifications')
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

  // Get notification icon component
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'rate_change':
        return (
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: 'linear-gradient(135deg,#357ABD,#4A90D9)' }}
          >
            <TrendingUp className="w-4 h-4 text-white" />
          </div>
        )
      case 'deadline':
        return (
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: 'linear-gradient(135deg,#D4A843,#E8C066)' }}
          >
            <Clock className="w-4 h-4 text-white" />
          </div>
        )
      case 'new_program':
        return (
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: 'linear-gradient(135deg,#0D9488,#14B8A6)' }}
          >
            <Zap className="w-4 h-4 text-white" />
          </div>
        )
      default:
        return (
          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-gray-200">
            <Bell className="w-4 h-4 text-white" />
          </div>
        )
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <>
      <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      <div>
        {/* Page Hero */}
        <div className="page-hero">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex items-center justify-between">
            <div className="flex items-center">
              <Bell className="w-8 h-8 text-brand-teal mr-3" />
              <h1 className="text-2xl font-bold text-white">Notifications</h1>
              {unreadCount > 0 && (
                <span className="badge badge-teal ml-3">{unreadCount} unread</span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                className="btn"
                style={{ background: 'rgba(255,255,255,0.1)', color: '#fff' }}
                onClick={handleMarkAllAsRead}
              >
                Mark All Read
              </button>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

          {/* Filter Bar */}
          <div className="card p-4 mb-6 flex flex-wrap items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={unreadOnly}
                onChange={(e) => {
                  setUnreadOnly(e.target.checked)
                  setPage(1)
                }}
                className="w-4 h-4 accent-brand-teal rounded"
              />
              <span className="text-sm font-medium text-gray-700">Unread only</span>
              {unreadCount > 0 && (
                <span className="badge badge-teal text-[10px]">{unreadCount}</span>
              )}
            </label>

            <div className="flex items-center gap-2">
              <label htmlFor="type-filter" className="text-sm font-medium text-gray-700">
                Type:
              </label>
              <select
                id="type-filter"
                value={selectedType}
                onChange={(e) => {
                  setSelectedType(e.target.value)
                  setPage(1)
                }}
                className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-brand-teal focus:border-transparent"
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
            <div className="callout-red mb-4 flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="ml-4 text-lg font-bold leading-none opacity-70 hover:opacity-100"
              >
                &times;
              </button>
            </div>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-4">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-teal border-t-transparent" />
              <p className="text-sm text-gray-500">Loading notifications...</p>
            </div>
          ) : (
            <>
              {/* Empty State */}
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20">
                  <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
                    style={{ background: 'linear-gradient(135deg,#0D9488,#14B8A6)' }}>
                    <Bell className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-brand-navy mb-2">No notifications</h3>
                  <p className="text-sm text-gray-500 text-center max-w-xs">
                    {unreadOnly
                      ? 'You have no unread notifications'
                      : "You haven't received any notifications yet"}
                  </p>
                  {!unreadOnly && (
                    <p className="text-sm text-brand-teal font-medium mt-2">You're all caught up!</p>
                  )}
                </div>
              ) : (
                /* Notifications List */
                <div className="flex flex-col gap-3">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`card p-4 flex items-start gap-4 hover:shadow-card-hover transition-all cursor-pointer${
                        !notification.is_read ? ' border-l-4 border-brand-teal' : ''
                      }`}
                    >
                      {/* Icon */}
                      {getNotificationIcon(notification.type)}

                      {/* Body */}
                      <div
                        className="flex-1 min-w-0"
                        onClick={() => handleNotificationClick(notification)}
                      >
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="font-semibold text-brand-navy text-sm">
                            {notification.title}
                          </h3>
                          {!notification.is_read && (
                            <span className="badge badge-teal text-[10px]">New</span>
                          )}
                        </div>

                        <p className="text-sm text-gray-600 mt-0.5 leading-relaxed">
                          {notification.message}
                        </p>

                        <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                          <span>{formatDate(notification.created_at)}</span>
                          {notification.link && (
                            <span>Click to view &#8594;</span>
                          )}
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex items-center gap-1 flex-shrink-0">
                        {!notification.is_read && (
                          <button
                            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-brand-navy"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleMarkAsRead(notification.id)
                            }}
                            title="Mark as read"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-brand-navy"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDelete(notification.id)
                          }}
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center gap-3 mt-6 justify-center">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="btn btn-outline px-4 py-2 disabled:opacity-40"
                  >
                    Previous
                  </button>

                  <span className="text-sm text-gray-500">
                    Page {page} of {totalPages}
                  </span>

                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="btn btn-outline px-4 py-2 disabled:opacity-40"
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
