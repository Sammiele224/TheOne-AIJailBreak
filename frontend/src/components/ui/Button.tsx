import { cloneElement, forwardRef, isValidElement } from 'react'

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  asChild?: boolean
}

const classes = {
  primary: 'bg-neon-cyan text-[#031019] shadow-[0_0_30px_rgba(78,246,255,0.2)]',
  secondary: 'border border-cyber-border bg-white/5 text-white hover:bg-white/10',
  ghost: 'border border-transparent bg-transparent text-text-muted hover:text-white hover:bg-white/5',
}

const sizes = {
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2.5 text-sm',
  lg: 'px-5 py-3 text-base',
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className = '', variant = 'primary', size = 'md', type = 'button', asChild = false, children, ...props },
  ref,
) {
  const buttonClasses = `inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-60 ${classes[variant]} ${sizes[size]} ${className}`

  // Style the child element directly instead of nesting it inside a <button>,
  // which would be invalid markup for an interactive child such as a <Link>.
  if (asChild && isValidElement<{ className?: string }>(children)) {
    return cloneElement(children, {
      className: `${buttonClasses} ${children.props.className ?? ''}`.trim(),
    })
  }

  return (
    <button ref={ref} type={type} className={buttonClasses} {...props}>
      {children}
    </button>
  )
})

export default Button
