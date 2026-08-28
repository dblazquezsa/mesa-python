from experimento import run_montecarlo, barrido_N2

def main():
    print("=== Ejecutando barrido de ejemplo ===")
    barrido_N2(
        n_runs=25,
        N2_min=474,
        N2_max=550,
        paso=2,
        salida="barrido.xlsx"
    )

if __name__ == "__main__":
    main()
