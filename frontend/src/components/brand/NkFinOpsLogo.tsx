interface Props {
  size?: number
  className?: string
}

export default function NkFinOpsLogo({ size = 22, className = '' }: Props) {
  return (
    <svg
      viewBox="0 0 220 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ height: size, width: 'auto' }}
      className={className}
    >
      <rect x="0" y="6" width="6" height="20" rx="1.5" fill="#7C3AED" />
      <rect x="10" y="6" width="6" height="20" rx="1.5" fill="#06B6D4" />
      <text
        x="26"
        y="24"
        fontFamily="Inter, sans-serif"
        fontWeight={800}
        fontSize={22}
        fill="white"
        letterSpacing="0.5"
      >
        NkFinOps
      </text>
    </svg>
  )
}
