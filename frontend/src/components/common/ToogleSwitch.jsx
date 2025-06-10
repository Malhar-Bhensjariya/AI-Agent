import React from 'react'

const ToggleSwitch = ({ 
  isOn, 
  onToggle, 
  label = '', 
  size = 'medium',
  disabled = false 
}) => {
  const sizeClasses = {
    small: {
      container: 'w-8 h-4',
      toggle: 'w-3 h-3',
      translate: 'translate-x-4'
    },
    medium: {
      container: 'w-12 h-6',
      toggle: 'w-5 h-5',
      translate: 'translate-x-6'
    },
    large: {
      container: 'w-14 h-7',
      toggle: 'w-6 h-6',
      translate: 'translate-x-7'
    }
  }

  const currentSize = sizeClasses[size]

  return (
    <div className="flex items-center space-x-3">
      {label && (
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <button
        type="button"
        onClick={onToggle}
        disabled={disabled}
        className={`
          ${currentSize.container}
          relative inline-flex items-center rounded-full
          transition-colors duration-200 ease-in-out
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          ${isOn ? 'bg-blue-600' : 'bg-gray-300'}
        `}
      >
        <span
          className={`
            ${currentSize.toggle}
            inline-block rounded-full bg-white shadow transform
            transition-transform duration-200 ease-in-out
            ${isOn ? currentSize.translate : 'translate-x-0.5'}
          `}
        />
      </button>
    </div>
  )
}

export default ToggleSwitch