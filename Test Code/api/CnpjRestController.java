@RestController
@RequestMapping("/api/v1/cnpj")
public class CnpjRestController {
    
    @GetMapping("/{cnpj}")
    public ResponseEntity<EmpresaDTO> consultarPorCnpj(@PathVariable long cnpj) {
        // Valida CNPJ numérico
        if (cnpj > 99999999999999L) {
            throw new IllegalArgumentException("CNPJ inválido");
        }
        
        return ResponseEntity.ok(new EmpresaDTO(cnpj));
    }

    @GetMapping("/filiais/{cnpjMatriz}")
    public List<Long> listarFiliais(@PathVariable long cnpjMatriz) {
        // Extrai base numérica da matriz
        long baseMatriz = cnpjMatriz / 10000;
        return filiaisRepository.findByCnpjStartingWith(baseMatriz);
    }

    @PostMapping("/validar-lote")
    public Map<Long, Boolean> validarLoteCnpj(@RequestBody List<Long> cnpjs) {
        return cnpjs.stream()
            .collect(Collectors.toMap(
                cnpj -> cnpj,
                cnpj -> (cnpj % 100) == calcularDV(cnpj / 100)
            ));
    }
}
